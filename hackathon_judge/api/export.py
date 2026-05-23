import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hackathon_judge.db.engine import get_db
from hackathon_judge.db.models import (
    EvaluationRun,
    HardRule,
    HardRuleResult,
    Project,
    ProjectScore,
    Rubric,
)

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/hackathons/{hackathon_id}/export")
async def export_excel(hackathon_id: int, run_id: int | None = None, db: AsyncSession = Depends(get_db)):
    if run_id is None:
        result = await db.execute(
            select(EvaluationRun)
            .where(EvaluationRun.hackathon_id == hackathon_id, EvaluationRun.status == "completed")
            .order_by(EvaluationRun.id.desc())
            .limit(1)
        )
        run = result.scalar_one_or_none()
        if not run:
            raise HTTPException(404, "No completed evaluation run found")
        run_id = run.id

    project_result = await db.execute(select(Project).where(Project.hackathon_id == hackathon_id))
    projects = {p.id: p for p in project_result.scalars().all()}

    rubric_result = await db.execute(
        select(Rubric).where(Rubric.hackathon_id == hackathon_id, Rubric.is_active == True)
    )
    rubrics = list(rubric_result.scalars().all())
    dimensions = [r.dimension for r in rubrics]
    weights = {r.dimension: r.weight for r in rubrics}

    score_result = await db.execute(select(ProjectScore).where(ProjectScore.evaluation_run_id == run_id))
    scores = list(score_result.scalars().all())

    hr_result = await db.execute(select(HardRuleResult).where(HardRuleResult.evaluation_run_id == run_id))
    hr_results = list(hr_result.scalars().all())

    rule_result = await db.execute(select(HardRule).where(HardRule.hackathon_id == hackathon_id))
    rules = {r.id: r for r in rule_result.scalars().all()}

    wb = Workbook()
    ws = wb.active
    ws.title = "Leaderboard"

    headers = ["Rank", "Project", "Weighted Score"] + [f"{d} ({weights.get(d, 0):.0%})" for d in dimensions] + ["Hard Rules"]
    ws.append(headers)

    project_scores: dict[int, dict] = {}
    for s in scores:
        project_scores.setdefault(s.project_id, {})[s.dimension] = s.score

    project_hr: dict[int, list] = {}
    for hr in hr_results:
        project_hr.setdefault(hr.project_id, []).append(hr)

    rows = []
    for pid, dim_scores in project_scores.items():
        if pid not in projects:
            continue
        total_weight = sum(weights.values()) or 1
        weighted = sum(dim_scores.get(d, 0) * weights.get(d, 0) for d in dimensions) / total_weight
        hr_list = project_hr.get(pid, [])
        hr_pass = sum(1 for hr in hr_list if hr.passed)
        rows.append((pid, weighted, dim_scores, hr_pass, len(hr_list)))

    rows.sort(key=lambda r: r[1], reverse=True)

    for rank, (pid, weighted, dim_scores, hr_pass, hr_total) in enumerate(rows, 1):
        row = [rank, projects[pid].title, round(weighted, 4)]
        for d in dimensions:
            row.append(round(dim_scores.get(d, 0), 4))
        row.append(f"{hr_pass}/{hr_total}" if hr_total else "N/A")
        ws.append(row)

    detail_ws = wb.create_sheet("Details")
    detail_ws.append(["Project", "Dimension", "Score", "Raw Score", "Reasoning", "Model"])
    for s in scores:
        if s.project_id in projects:
            detail_ws.append([
                projects[s.project_id].title,
                s.dimension,
                round(s.score, 4),
                round(s.raw_score, 4),
                s.reasoning or "",
                s.model_used or "",
            ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=hackathon_results.xlsx"},
    )
