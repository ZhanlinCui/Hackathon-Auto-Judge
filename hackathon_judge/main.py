from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hackathon_judge.api import config, evaluations, export, projects, rubrics
from hackathon_judge.db.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _seed_defaults()
    yield


app = FastAPI(title="Hackathon Judge", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(rubrics.router)
app.include_router(evaluations.router)
app.include_router(config.router)
app.include_router(export.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


async def _seed_defaults():
    from sqlalchemy import select

    from hackathon_judge.db.engine import async_session
    from hackathon_judge.db.models import Hackathon, Rubric
    from hackathon_judge.rubrics.defaults import DEFAULT_RUBRICS

    async with async_session() as session:
        result = await session.execute(select(Hackathon))
        if result.scalar_one_or_none() is not None:
            return

        h = Hackathon(name="Default Hackathon", description="Auto-created hackathon")
        session.add(h)
        await session.commit()
        await session.refresh(h)

        for rubric_def in DEFAULT_RUBRICS:
            r = Rubric(hackathon_id=h.id, **rubric_def)
            session.add(r)
        await session.commit()
