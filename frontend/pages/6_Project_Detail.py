import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import get_leaderboard, get_project, get_project_data, get_scores, list_hackathons, list_projects

st.set_page_config(page_title="Project Detail - Hackathon Auto Judge", layout="wide")
st.title("📄 Project Detail")

try:
    hackathons = list_hackathons()
except Exception as e:
    st.error(f"Cannot connect to backend: {e}")
    st.stop()

if not hackathons:
    st.stop()

hid = hackathons[0]["id"]
projects = list_projects(hid)

if not projects:
    st.info("No projects found. Import projects first on the **Import** page.")
    st.stop()

project_map = {p["id"]: p["title"] for p in projects}
selected_id = st.selectbox("Select Project", options=list(project_map.keys()), format_func=lambda x: project_map[x])

if selected_id:
    project = get_project(selected_id)

    st.subheader(project["title"])

    col1, col2 = st.columns(2)
    with col1:
        if project.get("github_url"):
            st.markdown(f"🔗 **GitHub:** [{project['github_url']}]({project['github_url']})")
        if project.get("demo_url"):
            st.markdown(f"🌐 **Demo:** [{project['demo_url']}]({project['demo_url']})")

        STATUS_COLORS = {"done": "🟢", "pending": "🟡", "scraping": "🔵", "error": "🔴", "no_repo": "⚪"}
        icon = STATUS_COLORS.get(project.get("scrape_status", ""), "⚪")
        st.markdown(f"**Scrape Status:** {icon} {project.get('scrape_status', 'N/A')}")
    with col2:
        if project.get("description"):
            st.markdown(f"**Description:** {project['description']}")
        if project.get("pitch_text"):
            st.markdown(f"**Pitch:** {project['pitch_text']}")

    # --- Evaluation Scores ---
    try:
        leaderboard = get_leaderboard(hid)
        latest_run_id = leaderboard[0]["run_id"] if leaderboard else None
        all_scores = get_scores(latest_run_id) if latest_run_id else []
        project_scores = [s for s in all_scores if s["project_id"] == selected_id]

        if project_scores:
            st.divider()
            st.subheader("Evaluation Scores / 评审评分")

            dimensions = [s["dimension"] for s in project_scores]
            scores = [s["score"] for s in project_scores]

            cols = st.columns(len(project_scores))
            for i, ps in enumerate(project_scores):
                with cols[i]:
                    st.metric(
                        ps["dimension"].capitalize(),
                        f"{ps['score']:.2%}",
                    )

            if len(dimensions) >= 3:
                import plotly.graph_objects as go

                r_vals = scores + [scores[0]]
                theta_vals = [d.capitalize() for d in dimensions] + [dimensions[0].capitalize()]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=r_vals, theta=theta_vals,
                    fill="toself", name=project["title"],
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    height=400,
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

            for ps in project_scores:
                with st.expander(f"📝 {ps['dimension'].capitalize()} — {ps['score']:.2%} (raw: {ps['raw_score']})"):
                    st.markdown(f"**Model:** `{ps.get('model_used', 'N/A')}`")
                    st.markdown("**Reasoning:**")
                    st.markdown(ps.get("reasoning", "No reasoning available."))
    except Exception:
        pass

    # --- Scraped Data ---
    pdata = get_project_data(selected_id)
    if pdata:
        st.divider()
        st.subheader("Scraped Data / 抓取数据")
        st.markdown(f"**Total Tokens:** {pdata.get('total_tokens', 0):,}")

        tabs = st.tabs(["README", "File Tree", "Config Files", "Source Files", "Commits"])

        with tabs[0]:
            readme = pdata.get("readme_content", "")
            if readme:
                st.markdown(readme)
            else:
                st.caption("No README content.")

        with tabs[1]:
            tree = pdata.get("file_tree")
            if isinstance(tree, str) and tree:
                st.code(tree, language=None)
            elif tree:
                st.json(tree)
            else:
                st.caption("No file tree data.")

        with tabs[2]:
            configs = pdata.get("config_files", {})
            if configs:
                for fpath, content in configs.items():
                    with st.expander(f"📄 {fpath}"):
                        st.code(content)
            else:
                st.caption("No config files.")

        with tabs[3]:
            sources = pdata.get("source_files", {})
            if sources:
                for fpath, content in sources.items():
                    with st.expander(f"📄 {fpath}"):
                        st.code(content)
            else:
                st.caption("No source files.")

        with tabs[4]:
            commits = pdata.get("commit_summary", [])
            if isinstance(commits, list) and commits:
                for c in commits:
                    st.markdown(f"- `{c.get('sha', '?')}` {c.get('message', '')} — *{c.get('author', '')}* ({c.get('date', '')})")
            else:
                st.caption("No commit data.")
