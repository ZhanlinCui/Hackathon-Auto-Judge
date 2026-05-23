import logging

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hackathon_judge.config.settings import get_app_config
from hackathon_judge.db.models import Hackathon, Project, ProjectData
from hackathon_judge.services.github_scraper import scrape_repo_async

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"title"}
OPTIONAL_COLUMNS = {"description", "github_url", "demo_url", "pitch_text"}


def parse_csv(content: bytes) -> list[dict]:
    df = pd.read_csv(pd.io.common.BytesIO(content))
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    projects = []
    for _, row in df.iterrows():
        proj = {"title": str(row["title"]).strip()}
        if not proj["title"]:
            continue
        for col in OPTIONAL_COLUMNS:
            if col in df.columns and pd.notna(row.get(col)):
                proj[col] = str(row[col]).strip()
            else:
                proj[col] = None
        projects.append(proj)

    return projects


async def import_projects(
    session: AsyncSession,
    hackathon_id: int,
    csv_content: bytes,
) -> list[Project]:
    parsed = parse_csv(csv_content)

    result = await session.execute(
        select(Hackathon).where(Hackathon.id == hackathon_id)
    )
    hackathon = result.scalar_one_or_none()
    if not hackathon:
        raise ValueError(f"Hackathon {hackathon_id} not found")

    projects = []
    for p in parsed:
        proj = Project(
            hackathon_id=hackathon_id,
            title=p["title"],
            description=p.get("description"),
            github_url=p.get("github_url"),
            demo_url=p.get("demo_url"),
            pitch_text=p.get("pitch_text"),
            scrape_status="pending" if p.get("github_url") else "no_repo",
        )
        session.add(proj)
        projects.append(proj)

    await session.commit()
    for proj in projects:
        await session.refresh(proj)

    return projects


async def scrape_project(session: AsyncSession, project: Project) -> ProjectData | None:
    if not project.github_url:
        project.scrape_status = "no_repo"
        await session.commit()
        return None

    token = (await get_app_config(session, "github_token")) or ""
    budget = int(await get_app_config(session, "token_budget") or "30000")

    project.scrape_status = "scraping"
    await session.commit()

    try:
        data = await scrape_repo_async(project.github_url, token, budget)

        existing = await session.execute(
            select(ProjectData).where(ProjectData.project_id == project.id)
        )
        pd_obj = existing.scalar_one_or_none()

        if pd_obj:
            pd_obj.readme_content = data["readme_content"]
            pd_obj.file_tree = data["file_tree"]
            pd_obj.config_files = data["config_files"]
            pd_obj.source_files = data["source_files"]
            pd_obj.commit_summary = data["commit_summary"]
            pd_obj.total_tokens = data["total_tokens"]
        else:
            pd_obj = ProjectData(
                project_id=project.id,
                readme_content=data["readme_content"],
                file_tree=data["file_tree"],
                config_files=data["config_files"],
                source_files=data["source_files"],
                commit_summary=data["commit_summary"],
                total_tokens=data["total_tokens"],
            )
            session.add(pd_obj)

        project.scrape_status = "done"
        await session.commit()
        return pd_obj

    except Exception as e:
        logger.error(f"Scrape failed for {project.title}: {e}")
        project.scrape_status = "error"
        await session.commit()
        return None
