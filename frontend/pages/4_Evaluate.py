import time

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import get_config, get_evaluation_run, list_hackathons, list_projects, list_rubrics, start_evaluation

st.set_page_config(page_title="Evaluate - Hackathon Judge", layout="wide")
st.title("🔬 Run Evaluation")

try:
    hackathons = list_hackathons()
except Exception as e:
    st.error(f"Cannot connect to backend: {e}")
    st.stop()

if not hackathons:
    st.warning("No hackathons found.")
    st.stop()

hid = hackathons[0]["id"]
projects = list_projects(hid)

if not projects:
    st.warning("No projects imported. Go to the **Import** page first.")
    st.stop()

scraped = [p for p in projects if p["scrape_status"] == "done"]

st.subheader("Pre-flight Check / 评审前检查")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Projects / 项目**")
    st.markdown(f"- Total: **{len(projects)}**")
    st.markdown(f"- Scraped (ready): **{len(scraped)}**")
    not_ready = len(projects) - len(scraped)
    if not_ready:
        st.warning(f"{not_ready} projects not scraped — they will be evaluated with limited context (pitch/description only, no code data).")

with col2:
    st.markdown("**Model & Dimensions / 模型与维度**")
    try:
        config_data = get_config()
        configs = config_data.get("configs", {})
        rubrics = list_rubrics(hid)
        active_rubrics = [r for r in rubrics if r.get("is_active", True)]

        model = configs.get("default_model", "gpt-4o-mini")
        st.markdown(f"- Default model: `{model}`")
        st.markdown(f"- Active dimensions: **{len(active_rubrics)}**")
        for r in active_rubrics:
            dim_model = configs.get(f"model_{r['dimension']}", "") or model
            st.markdown(f"  - {r['name']} ({r['weight']:.0%}) → `{dim_model}`")

        total_evals = len(projects) * len(active_rubrics)
        st.markdown(f"- Total LLM calls: **{total_evals}**")
    except Exception:
        st.caption("Cannot load config details.")

st.divider()

if "eval_run_id" not in st.session_state:
    st.session_state.eval_run_id = None

if st.button("🚀 Start Evaluation", type="primary", use_container_width=True):
    result = start_evaluation(hid)
    st.session_state.eval_run_id = result["id"]
    st.rerun()

if st.session_state.eval_run_id:
    run_id = st.session_state.eval_run_id
    st.subheader(f"Evaluation Run #{run_id}")

    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    for _ in range(300):
        run = get_evaluation_run(run_id)
        eval_status = run["status"]
        total = run["total_count"] or 1
        completed = run["completed_count"]

        pct = min(completed / total, 1.0)
        progress_bar.progress(pct)
        status_placeholder.markdown(
            f"**Status:** {eval_status} | **Progress:** {completed}/{total} ({pct:.0%})"
        )

        if eval_status in ("completed", "completed_with_errors", "error"):
            break
        time.sleep(2)

    if run["status"] == "completed":
        st.success("✅ Evaluation completed! Go to the **Leaderboard** page to view results.")
        st.session_state.eval_run_id = None
    elif run["status"] == "completed_with_errors":
        st.warning("⚠️ Evaluation completed with some errors. Partial results are available on the **Leaderboard** page. Check server logs for details.")
        st.session_state.eval_run_id = None
    elif run["status"] == "error":
        st.error("Evaluation encountered an error. Check server logs for details.")
        st.session_state.eval_run_id = None
