import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from hackathon_judge.config.settings import get_all_app_config, get_app_config, set_app_config
from hackathon_judge.db.engine import get_db
from hackathon_judge.schemas.config import ConfigOut, ConfigUpdate

router = APIRouter(prefix="/api", tags=["config"])

ALLOWED_CONFIG_KEYS = {
    "openai_api_key", "anthropic_api_key", "gemini_api_key", "deepseek_api_key",
    "github_token",
    "default_model", "model_technical", "model_feature", "model_uiux", "model_freshness",
    "concurrency", "token_budget",
}

_SENSITIVE_SUFFIXES = ("_api_key", "_token")


def _mask_sensitive(configs: dict[str, str]) -> dict[str, str]:
    masked = {}
    for key, value in configs.items():
        if any(key.endswith(s) for s in _SENSITIVE_SUFFIXES) and value:
            masked[key] = value[:4] + "..." + value[-4:] if len(value) > 12 else "****"
        else:
            masked[key] = value
    return masked


@router.get("/config", response_model=ConfigOut)
async def get_config(db: AsyncSession = Depends(get_db)):
    configs = await get_all_app_config(db)
    return ConfigOut(configs=_mask_sensitive(configs))


@router.put("/config")
async def update_config(body: ConfigUpdate, db: AsyncSession = Depends(get_db)):
    if body.key not in ALLOWED_CONFIG_KEYS:
        raise HTTPException(400, f"Unknown config key: {body.key}")
    await set_app_config(db, body.key, body.value)
    return {"message": "Updated"}


@router.put("/config/batch")
async def update_config_batch(items: list[ConfigUpdate], db: AsyncSession = Depends(get_db)):
    for item in items:
        if item.key not in ALLOWED_CONFIG_KEYS:
            raise HTTPException(400, f"Unknown config key: {item.key}")
    for item in items:
        await set_app_config(db, item.key, item.value)
    return {"message": f"Updated {len(items)} configs"}


@router.post("/config/test")
async def test_llm_connection(db: AsyncSession = Depends(get_db)):
    import litellm

    key_map = {
        "openai_api_key": "OPENAI_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "deepseek_api_key": "DEEPSEEK_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY",
    }
    for config_key, env_var in key_map.items():
        value = await get_app_config(db, config_key)
        if value:
            os.environ[env_var] = value

    model = await get_app_config(db, "default_model") or "gpt-4o-mini"
    try:
        resp = await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5,
        )
        return {"status": "ok", "model": model, "response": resp.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "model": model, "error": str(e)}
