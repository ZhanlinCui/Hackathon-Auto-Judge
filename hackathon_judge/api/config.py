from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from hackathon_judge.config.settings import get_all_app_config, set_app_config
from hackathon_judge.db.engine import get_db
from hackathon_judge.schemas.config import ConfigOut, ConfigUpdate

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config", response_model=ConfigOut)
async def get_config(db: AsyncSession = Depends(get_db)):
    configs = await get_all_app_config(db)
    return ConfigOut(configs=configs)


@router.put("/config")
async def update_config(body: ConfigUpdate, db: AsyncSession = Depends(get_db)):
    await set_app_config(db, body.key, body.value)
    return {"message": "Updated"}


@router.put("/config/batch")
async def update_config_batch(items: list[ConfigUpdate], db: AsyncSession = Depends(get_db)):
    for item in items:
        await set_app_config(db, item.key, item.value)
    return {"message": f"Updated {len(items)} configs"}
