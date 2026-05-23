import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from hackathon_judge.db.engine import get_db
from hackathon_judge.db.models import (
    EvaluationRun,
    HardRule,
    HardRuleResult,
    Project,
    ProjectScore,
    Rubric,
)
from hackathon_judge.schemas.evaluation import (
    EvaluationRunOut,
    HardRuleResultOut,
    LeaderboardEntry,
    ProjectScoreOut,
)
from hackathon_judge.services.evaluation_engine import run_evaluation

router = APIRouter(prefix="/api", tags=["evaluations"])


@router.post("/hackathons/{hackathon_id}/evaluate", response_model=EvaluationRunOut)
async def start_evaluation(hackathon_id: int, db: AsyncSession = Depends(get_db)):
    config_snapshot = {}
    run = EvaluationRun(
        hackathon_id=hackathon_id,
        status="pending",
        model_config_snapshot=config_snapshot,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    asyncio.create_task(run_evaluation(db, hackathon_id, run.id))
    return run


@router.get("/evaluation-runs/{run_id}", response_model=EvaluationRunOut)
async def get_evaluation_run(run_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EvaluationRun).where(EvaluationRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(404, "Evaluation run not found")
    return run


@router.get("/evaluation-runs/{run_id}/scores", response_model=list[ProjectScoreOut])
async def get_scores(run_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectScore).where(ProjectScore.evaluation_run_id == run_id)
    )
    return list(result.scalars().all())


@router.get("/evaluation-runs/{run_id}/hard-rule-results", response_model=list[HardRuleResultOut])
async def get_hard_rule_results(run_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HardRuleResult).where(HardRuleResult.evaluation_run_id == run_id)
    )
    return list(result.scalars().all())


@router.get("/hackathons/{hackathon_id}/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(hackathon_id: int, run_id: int | None = None, db: AsyncSession = Depends(get_db)):
    if run_id is None:
        result = await db.execute(
            select(EvaluationRun)
            .where(EvaluationRun.hackathon_id == hackathon_id, EvaluationRun.status == "completed")
            .order_by(EvaluationRun.id.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()
        if not latest_run:
            return []
        run_id = latest_run.id

    rubric_result = await db.execute(
        select(Rubric).where(Rubric.hackathon_id == hackathon_id, Rubric.is_active == True)
    )
    rubrics = {r.dimension: r.weight for r in rubric_result.scalars().all()}

    project_result = await db.execute(
        select(Project).where(Project.hackathon_id == hackathon_id)
    )
    projects = {p.id: p for p in project_result.scalars().all()}

    score_result = await db.execute(
        select(ProjectScore).where(ProjectScore.evaluation_run_id == run_id)
    )
    scores = list(score_result.scalars().all())

    hr_result = await db.execute(
        select(HardRuleResult).where(HardRuleResult.evaluation_run_id == run_id)
    )
    hr_results = list(hr_result.scalars().all())

    rule_result = await db.execute(
        select(HardRule).where(HardRule.hackathon_id == hackathon_id)
    )
    total_rules = len(list(rule_result.scalars().all()))

    project_scores: dict[int, dict[str, float]] = {}
    for s in scores:
        project_scores.setdefault(s.project_id, {})[s.dimension] = s.score

    project_hr: dict[int, int] = {}
    for hr in hr_results:
        if hr.passed:
            project_hr[hr.project_id] = project_hr.get(hr.project_id, 0) + 1

    entries = []
    for pid, dim_scores in project_scores.items():
        if pid not in projects:
            continue
        weighted = sum(dim_scores.get(dim, 0) * w for dim, w in rubrics.items())
        total_weight = sum(rubrics.values()) or 1
        entries.append(LeaderboardEntry(
            project_id=pid,
            title=projects[pid].title,
            weighted_score=round(weighted / total_weight, 4),
            dimension_scores={k: round(v, 4) for k, v in dim_scores.items()},
            hard_rules_passed=project_hr.get(pid, 0),
            hard_rules_total=total_rules,
        ))

    entries.sort(key=lambda e: e.weighted_score, reverse=True)
    return entries
