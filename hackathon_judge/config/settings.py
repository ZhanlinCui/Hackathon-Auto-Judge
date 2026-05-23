import json
from functools import lru_cache

from pydantic_settings import BaseSettings
from sqlalchemy import select

from hackathon_judge.db.models import AppConfig


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/hackathon.db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    github_token: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    gemini_api_key: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


CONFIG_DEFAULTS = {
    "default_model": "gpt-4o-mini",
    "concurrency": "3",
    "token_budget": "30000",
    "model_technical": "",
    "model_feature": "",
    "model_uiux": "",
    "model_freshness": "",
}


async def get_app_config(session, key: str) -> str | None:
    result = await session.execute(select(AppConfig).where(AppConfig.key == key))
    row = result.scalar_one_or_none()
    if row:
        return row.value
    return CONFIG_DEFAULTS.get(key)


async def set_app_config(session, key: str, value: str):
    result = await session.execute(select(AppConfig).where(AppConfig.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = value
    else:
        session.add(AppConfig(key=key, value=value))
    await session.commit()


async def get_all_app_config(session) -> dict[str, str]:
    result = await session.execute(select(AppConfig))
    rows = {r.key: r.value for r in result.scalars().all()}
    merged = {**CONFIG_DEFAULTS, **rows}
    return merged


async def get_model_for_dimension(session, dimension: str) -> str:
    dim_key = f"model_{dimension}"
    model = await get_app_config(session, dim_key)
    if model:
        return model
    return await get_app_config(session, "default_model") or CONFIG_DEFAULTS["default_model"]
