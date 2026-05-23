import streamlit as st

st.set_page_config(page_title="Hackathon Judge", page_icon="⚖️", layout="wide")

st.title("⚖️ Hackathon Judge")
st.caption("AI-Powered Hackathon Project Evaluation Platform")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🔬 LLM Evaluation")
    st.markdown("Uses deepeval GEval metrics to evaluate projects across multiple dimensions with any LLM provider.")

with col2:
    st.markdown("### 📊 Multi-Dimension")
    st.markdown("4 default dimensions: Technical Soundness, Feature Alignment, UI/UX Innovation, Code Freshness.")

with col3:
    st.markdown("### 🔗 GitHub Integration")
    st.markdown("Auto-scrapes GitHub repos — file tree, source code, config files, commit history — with token budget control.")

with col4:
    st.markdown("### 🏆 Leaderboard")
    st.markdown("Weighted scoring, radar charts, per-project reasoning, and Excel export for offline review.")

st.markdown("---")

st.subheader("How It Works")

st.markdown("""
```
CSV Import → GitHub Scrape → LLM Evaluation (deepeval GEval) → Leaderboard
```

1. **Import** — Upload a CSV with project info (title, GitHub URL, description)
2. **Scrape** — The system fetches README, source code, config files, and commit history via GitHub API
3. **Evaluate** — Each project is scored by an LLM across customizable dimensions using [deepeval](https://github.com/confident-ai/deepeval) GEval metrics
4. **Review** — View the leaderboard, read per-dimension reasoning, and export results to Excel
""")

st.markdown("---")

st.subheader("Quick Start")
st.markdown("""
1. **⚙️ Config** — Set your LLM API key and GitHub token
2. **📋 Rubrics** — Review evaluation dimensions and weights (or customize them)
3. **📥 Import** — Upload project CSV and scrape GitHub repos
4. **🔬 Evaluate** — Run AI-powered evaluation
5. **🏆 Leaderboard** — View ranked results and export
""")

st.markdown("---")

st.subheader("Supported LLM Providers")
st.markdown("""
Via [LiteLLM](https://github.com/BerriAI/litellm), any major LLM provider is supported:

| Provider | Model Example | Env Var |
|----------|--------------|---------|
| OpenAI | `gpt-4o`, `gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| Google Gemini | `gemini/gemini-2.5-flash` | `GEMINI_API_KEY` |
| DeepSeek | `deepseek/deepseek-chat` | `DEEPSEEK_API_KEY` |
""")

st.markdown("---")

try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from api_client import health
    status = health()
    st.success(f"✅ Backend connected (status: {status.get('status', 'unknown')})")
except Exception:
    st.error("❌ Cannot connect to backend. Make sure the API server is running on port 8000.")
    st.code("uvicorn hackathon_judge.main:app --host 127.0.0.1 --port 8000", language="bash")
