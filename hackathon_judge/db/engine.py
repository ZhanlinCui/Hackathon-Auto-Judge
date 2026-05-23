from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hackathon_judge.config.settings import get_settings

engine = create_async_engine(get_settings().database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    from hackathon_judge.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
