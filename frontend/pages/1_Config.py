import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import get_config, update_config_batch

st.set_page_config(page_title="Config - Hackathon Judge", layout="wide")
st.title("Configuration")

try:
    config_data = get_config()
    configs = config_data.get("configs", {})
except Exception as e:
    st.error(f"Cannot load config: {e}")
    st.stop()

st.subheader("LLM API Keys")
st.info("Set at least one API key. Keys are stored in the local database. Leave blank to keep existing key unchanged.")

_SENSITIVE_KEYS = {"openai_api_key", "anthropic_api_key", "gemini_api_key", "deepseek_api_key", "github_token"}


def _has_key(key: str) -> bool:
    val = configs.get(key, "")
    return bool(val) and val != "****"


col1, col2 = st.columns(2)

with col1:
    openai_key = st.text_input(
        "OpenAI API Key",
        value="",
        type="password",
        placeholder="Configured" if _has_key("openai_api_key") else "Not set",
        help="Get from https://platform.openai.com/api-keys",
    )
    anthropic_key = st.text_input(
        "Anthropic API Key",
        value="",
        type="password",
        placeholder="Configured" if _has_key("anthropic_api_key") else "Not set",
        help="Get from https://console.anthropic.com/",
    )

with col2:
    gemini_key = st.text_input(
        "Google Gemini API Key",
        value="",
        type="password",
        placeholder="Configured" if _has_key("gemini_api_key") else "Not set",
        help="Get from https://aistudio.google.com/apikey",
    )
    deepseek_key = st.text_input(
        "DeepSeek API Key",
        value="",
        type="password",
        placeholder="Configured" if _has_key("deepseek_api_key") else "Not set",
        help="Get from https://platform.deepseek.com/",
    )

st.divider()
st.subheader("GitHub Token")
st.info("Required for scraping GitHub repos. Without a token, rate limit is 60 requests/hour.")

github_token = st.text_input(
    "GitHub Personal Access Token",
    value="",
    type="password",
    placeholder="Configured" if _has_key("github_token") else "Not set",
    help="Create at https://github.com/settings/tokens",
)

st.divider()
st.subheader("Model Settings")

COMMON_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.5-pro",
    "anthropic/claude-sonnet-4-20250514",
    "deepseek/deepseek-chat",
]

current_default = configs.get("default_model", "gpt-4o-mini")
if current_default in COMMON_MODELS:
    default_idx = COMMON_MODELS.index(current_default)
else:
    COMMON_MODELS.append(current_default)
    default_idx = len(COMMON_MODELS) - 1

default_model = st.selectbox(
    "Default Model",
    options=COMMON_MODELS,
    index=default_idx,
    help="Model used for all dimensions unless overridden below. Uses LiteLLM format: provider/model-name",
)

st.markdown("**Per-dimension model overrides** (leave empty to use default)")
col1, col2 = st.columns(2)
with col1:
    model_technical = st.text_input("Technical Soundness model", value=configs.get("model_technical", ""), help="e.g. gpt-4o")
    model_feature = st.text_input("Feature Alignment model", value=configs.get("model_feature", ""), help="e.g. gemini/gemini-2.5-flash")
with col2:
    model_uiux = st.text_input("UI/UX Innovation model", value=configs.get("model_uiux", ""))
    model_freshness = st.text_input("Code Freshness model", value=configs.get("model_freshness", ""))

st.divider()
st.subheader("Evaluation Settings")

col1, col2 = st.columns(2)
with col1:
    concurrency = st.slider(
        "Concurrency",
        1, 10, int(configs.get("concurrency", "3")),
        help="Number of parallel LLM evaluation calls. Higher = faster but may hit rate limits.",
    )
with col2:
    token_budget = st.slider(
        "Token Budget per Project",
        5000, 100000, int(configs.get("token_budget", "30000")), step=5000,
        help="Max tokens of scraped content sent to LLM per project. Higher = more context but more cost.",
    )

st.divider()


def _build_save_items():
    items = []
    if openai_key:
        items.append({"key": "openai_api_key", "value": openai_key})
    if anthropic_key:
        items.append({"key": "anthropic_api_key", "value": anthropic_key})
    if gemini_key:
        items.append({"key": "gemini_api_key", "value": gemini_key})
    if deepseek_key:
        items.append({"key": "deepseek_api_key", "value": deepseek_key})
    if github_token:
        items.append({"key": "github_token", "value": github_token})
    items.extend([
        {"key": "default_model", "value": default_model},
        {"key": "model_technical", "value": model_technical},
        {"key": "model_feature", "value": model_feature},
        {"key": "model_uiux", "value": model_uiux},
        {"key": "model_freshness", "value": model_freshness},
        {"key": "concurrency", "value": str(concurrency)},
        {"key": "token_budget", "value": str(token_budget)},
    ])
    return items


col_save, col_test = st.columns([1, 1])

with col_save:
    if st.button("Save Configuration", type="primary", use_container_width=True):
        update_config_batch(_build_save_items())
        st.success("Configuration saved!")

with col_test:
    if st.button("Test LLM Connection", use_container_width=True):
        import httpx
        save_items = _build_save_items()
        if save_items:
            update_config_batch(save_items)
        try:
            resp = httpx.post(
                "http://127.0.0.1:8000/api/config/test",
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    st.success(f"LLM connection successful! Model: `{data.get('model')}`")
                else:
                    st.error(f"LLM connection failed: {data.get('error', 'Unknown error')}")
            else:
                st.warning("Test endpoint not available.")
        except Exception:
            st.warning("Cannot connect to backend. Is the server running?")
