import asyncio
import json
import logging
import os
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from hackathon_judge.config.settings import get_app_config, get_model_for_dimension
from hackathon_judge.db.engine import async_session
from hackathon_judge.db.models import (
    EvaluationRun,
    HardRule,
    HardRuleResult,
    Project,
    ProjectData,
    ProjectScore,
    Rubric,
)
from hackathon_judge.services.llm_provider import get_litellm_model

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

_API_KEY_CONFIG_KEYS = {
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "deepseek_api_key": "DEEPSEEK_API_KEY",
    "gemini_api_key": "GEMINI_API_KEY",
}


async def _load_api_keys_from_db(session: AsyncSession):
    for config_key, env_var in _API_KEY_CONFIG_KEYS.items():
        value = await get_app_config(session, config_key)
        if value:
            os.environ[env_var] = value
        else:
            os.environ.pop(env_var, None)


def _build_evaluation_input(project: Project, project_data: ProjectData | None, rubric: Rubric) -> tuple[str, str]:
    input_parts = []
    if project.pitch_text:
        input_parts.append(f"## Project Pitch\n{project.pitch_text}")
    if project.description:
        input_parts.append(f"## Project Description\n{project.description}")
    if project_data and project_data.readme_content:
        input_parts.append(f"## README\n{project_data.readme_content}")
    input_text = "\n\n".join(input_parts) if input_parts else "No project description available."

    output_parts = []
    if project_data:
        if project_data.file_tree:
            tree = project_data.file_tree if isinstance(project_data.file_tree, str) else json.dumps(project_data.file_tree)
            output_parts.append(f"## File Tree\n{tree}")
        if project_data.config_files:
            configs = project_data.config_files if isinstance(project_data.config_files, dict) else {}
            for path, content in configs.items():
                output_parts.append(f"## Config: {path}\n```\n{content}\n```")
        if project_data.source_files:
            sources = project_data.source_files if isinstance(project_data.source_files, dict) else {}
            for path, content in sources.items():
                output_parts.append(f"## Source: {path}\n```\n{content}\n```")
        if project_data.commit_summary:
            commits = project_data.commit_summary
            if isinstance(commits, list):
                commit_text = "\n".join(f"- {c.get('sha', '???')} {c.get('message', '')}" for c in commits)
                output_parts.append(f"## Commit History\n{commit_text}")

    actual_output = "\n\n".join(output_parts) if output_parts else "No code data available."

    return input_text, actual_output


async def _evaluate_single(
    project: Project,
    project_data: ProjectData | None,
    rubric: Rubric,
    model_name: str,
) -> dict:
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams

    input_text, actual_output = _build_evaluation_input(project, project_data, rubric)

    model = get_litellm_model(model_name)

    metric = GEval(
        name=rubric.name,
        criteria=rubric.criteria,
        evaluation_steps=rubric.evaluation_steps,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=model,
        threshold=0.5,
    )

    test_case = LLMTestCase(input=input_text, actual_output=actual_output)

    for attempt in range(MAX_RETRIES):
        try:
            await metric.a_measure(test_case)
            raw_score = metric.score if metric.score is not None else 0.0
            score = min(max(raw_score, 0.0), 1.0)
            return {
                "raw_score": raw_score,
                "score": score,
                "reasoning": metric.reason or "",
                "status": "done",
            }
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {project.title}/{rubric.dimension}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** attempt)

    return {"raw_score": 0.0, "score": 0.0, "reasoning": "Evaluation failed after retries", "status": "error"}


def _check_hard_rule(project_data: ProjectData | None, rule: HardRule) -> tuple[bool, str]:
    if not project_data:
        return False, "No project data available"

    if rule.check_type == "readme_contains":
        readme = project_data.readme_content or ""
        found = rule.check_value.lower() in readme.lower()
        return found, f"README {'contains' if found else 'does not contain'} '{rule.check_value}'"

    if rule.check_type == "file_exists":
        tree = project_data.file_tree or ""
        tree_str = tree if isinstance(tree, str) else json.dumps(tree)
        found = rule.check_value in tree_str
        return found, f"File '{rule.check_value}' {'found' if found else 'not found'} in tree"

    if rule.check_type == "commit_count_min":
        commits = project_data.commit_summary
        if isinstance(commits, list):
            count = len(commits)
            try:
                threshold = int(rule.check_value)
            except (ValueError, TypeError):
                return False, f"Invalid threshold value: '{rule.check_value}'"
            passed = count >= threshold
            return passed, f"Commit count: {count} (min: {threshold})"
        return False, "No commit data"

    return False, f"Unknown check type: {rule.check_type}"


async def run_evaluation(
    hackathon_id: int,
    evaluation_run_id: int,
):
    async with async_session() as session:
        try:
            await _load_api_keys_from_db(session)

            run_result = await session.execute(
                select(EvaluationRun).where(EvaluationRun.id == evaluation_run_id)
            )
            run = run_result.scalar_one()
            run.status = "running"
            run.started_at = datetime.now(UTC)
            await session.commit()

            rubric_result = await session.execute(
                select(Rubric).where(Rubric.hackathon_id == hackathon_id, Rubric.is_active == True)
            )
            rubrics = list(rubric_result.scalars().all())

            project_result = await session.execute(
                select(Project)
                .where(Project.hackathon_id == hackathon_id)
                .options(selectinload(Project.data))
            )
            projects = list(project_result.scalars().all())

            rule_result = await session.execute(
                select(HardRule).where(HardRule.hackathon_id == hackathon_id)
            )
            hard_rules = list(rule_result.scalars().all())

            run.total_count = len(projects) * len(rubrics)
            await session.commit()

            concurrency = int(await get_app_config(session, "concurrency") or "3")
            semaphore = asyncio.Semaphore(concurrency)

            project_rubric_args = []
            for project in projects:
                for rubric in rubrics:
                    model_name = await get_model_for_dimension(session, rubric.dimension)
                    project_rubric_args.append((project, project.data, rubric, model_name))

            for project in projects:
                for rule in hard_rules:
                    passed, detail = _check_hard_rule(project.data, rule)
                    hr_result = HardRuleResult(
                        evaluation_run_id=evaluation_run_id,
                        project_id=project.id,
                        hard_rule_id=rule.id,
                        passed=passed,
                        detail=detail,
                    )
                    session.add(hr_result)
                await session.commit()

            if not project_rubric_args:
                run.status = "completed"
                run.finished_at = datetime.now(UTC)
                await session.commit()
                return

        except Exception as e:
            logger.error(f"Evaluation setup failed: {e}")
            async with async_session() as err_session:
                res = await err_session.execute(
                    select(EvaluationRun).where(EvaluationRun.id == evaluation_run_id)
                )
                run = res.scalar_one()
                run.status = "error"
                run.finished_at = datetime.now(UTC)
                await err_session.commit()
            return

    async def evaluate_and_save(
        project: Project,
        project_data: ProjectData | None,
        rubric: Rubric,
        model_name: str,
    ):
        async with semaphore:
            result = await _evaluate_single(project, project_data, rubric, model_name)

            async with async_session() as task_session:
                score = ProjectScore(
                    evaluation_run_id=evaluation_run_id,
                    project_id=project.id,
                    dimension=rubric.dimension,
                    score=result["score"],
                    raw_score=result["raw_score"],
                    reasoning=result["reasoning"],
                    model_used=model_name,
                    tokens_used=0,
                    status=result["status"],
                )
                task_session.add(score)

                await task_session.execute(
                    update(EvaluationRun)
                    .where(EvaluationRun.id == evaluation_run_id)
                    .values(completed_count=EvaluationRun.completed_count + 1)
                )
                await task_session.commit()

            return result

    tasks = [
        evaluate_and_save(project, project_data, rubric, model_name)
        for project, project_data, rubric, model_name in project_rubric_args
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    error_count = sum(
        1 for r in results
        if isinstance(r, Exception) or (isinstance(r, dict) and r.get("status") == "error")
    )

    async with async_session() as session:
        run_result = await session.execute(
            select(EvaluationRun).where(EvaluationRun.id == evaluation_run_id)
        )
        run = run_result.scalar_one()

        if error_count == len(results):
            run.status = "error"
        elif error_count > 0:
            run.status = "completed_with_errors"
        else:
            run.status = "completed"

        run.finished_at = datetime.now(UTC)
        await session.commit()
