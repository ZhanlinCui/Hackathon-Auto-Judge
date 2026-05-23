import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from hackathon_judge.db.engine import get_db
from hackathon_judge.db.models import Hackathon, Project
from hackathon_judge.schemas.project import HackathonCreate, HackathonOut, ProjectDataOut, ProjectOut
from hackathon_judge.services.ingestion import import_projects, scrape_project

router = APIRouter(prefix="/api", tags=["projects"])


@router.post("/hackathons", response_model=HackathonOut)
async def create_hackathon(body: HackathonCreate, db: AsyncSession = Depends(get_db)):
    h = Hackathon(name=body.name, description=body.description)
    db.add(h)
    await db.commit()
    await db.refresh(h)
    return h


@router.get("/hackathons", response_model=list[HackathonOut])
async def list_hackathons(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hackathon))
    return list(result.scalars().all())


@router.get("/hackathons/{hackathon_id}", response_model=HackathonOut)
async def get_hackathon(hackathon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hackathon).where(Hackathon.id == hackathon_id))
    h = result.scalar_one_or_none()
    if not h:
        raise HTTPException(404, "Hackathon not found")
    return h


@router.get("/hackathons/{hackathon_id}/projects", response_model=list[ProjectOut])
async def list_projects(hackathon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.hackathon_id == hackathon_id))
    return list(result.scalars().all())


@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Project not found")
    return p


@router.get("/projects/{project_id}/data", response_model=ProjectDataOut | None)
async def get_project_data(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.data))
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Project not found")
    return p.data


@router.post("/hackathons/{hackathon_id}/import", response_model=list[ProjectOut])
async def import_csv(
    hackathon_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    try:
        projects = await import_projects(db, hackathon_id, content)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return projects


@router.post("/hackathons/{hackathon_id}/scrape")
async def scrape_all(hackathon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(
            Project.hackathon_id == hackathon_id,
            Project.scrape_status.in_(["pending", "error"]),
        )
    )
    projects = list(result.scalars().all())
    if not projects:
        return {"message": "No projects to scrape"}

    project_ids = [p.id for p in projects]

    async def do_scrape():
        from hackathon_judge.db.engine import async_session

        for pid in project_ids:
            async with async_session() as session:
                res = await session.execute(select(Project).where(Project.id == pid))
                project = res.scalar_one_or_none()
                if project:
                    await scrape_project(session, project)

    asyncio.create_task(do_scrape())
    return {"message": f"Scraping {len(projects)} projects in background"}
