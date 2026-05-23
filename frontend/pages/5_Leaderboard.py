import pandas as pd
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import export_excel, get_leaderboard, get_scores, list_hackathons

st.set_page_config(page_title="Leaderboard - Hackathon Judge", layout="wide")
st.title("🏆 Leaderboard")

try:
    hackathons = list_hackathons()
except Exception as e:
    st.error(f"Cannot connect to backend: {e}")
    st.stop()

if not hackathons:
    st.warning("No hackathons found.")
    st.stop()

hid = hackathons[0]["id"]
leaderboard = get_leaderboard(hid)

if not leaderboard:
    st.info("No evaluation results yet. Run an evaluation first on the **Evaluate** page.")
    st.stop()

dimensions = list(leaderboard[0]["dimension_scores"].keys()) if leaderboard else []

sort_options = ["Weighted Score"] + [d.capitalize() for d in dimensions]
sort_by = st.selectbox("Sort by", sort_options, index=0)

if sort_by == "Weighted Score":
    leaderboard.sort(key=lambda e: e["weighted_score"], reverse=True)
else:
    dim_key = sort_by.lower()
    leaderboard.sort(key=lambda e: e["dimension_scores"].get(dim_key, 0), reverse=True)

rows = []
for rank, entry in enumerate(leaderboard, 1):
    row = {
        "Rank": rank,
        "Project": entry["title"],
        "Score": entry["weighted_score"],
    }
    for dim in dimensions:
        row[dim.capitalize()] = entry["dimension_scores"].get(dim, 0)
    hr_total = entry["hard_rules_total"]
    row["Hard Rules"] = f"{entry['hard_rules_passed']}/{hr_total}" if hr_total > 0 else "—"
    rows.append(row)

df = pd.DataFrame(rows)

score_cols = ["Score"] + [d.capitalize() for d in dimensions]

def highlight_scores(val):
    if isinstance(val, (int, float)):
        if val >= 0.8:
            return "background-color: #c6efce; color: #006100"
        elif val >= 0.5:
            return "background-color: #ffeb9c; color: #9c6500"
        elif val > 0:
            return "background-color: #ffc7ce; color: #9c0006"
    return ""

styled = df.style.applymap(highlight_scores, subset=score_cols).format(
    {col: "{:.2%}" for col in score_cols}
)

st.dataframe(styled, use_container_width=True, hide_index=True)

col_export, col_spacer = st.columns([1, 4])
with col_export:
    excel_bytes = export_excel(hid)
    if excel_bytes:
        st.download_button(
            "📥 Export Excel",
            data=excel_bytes,
            file_name="hackathon_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

st.divider()
st.subheader("Dimension Comparison / 维度对比")

if len(leaderboard) > 0 and len(dimensions) >= 3:
    import plotly.graph_objects as go

    fig = go.Figure()
    for entry in leaderboard:
        scores = [entry["dimension_scores"].get(d, 0) for d in dimensions]
        scores.append(scores[0])
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=[d.capitalize() for d in dimensions] + [dimensions[0].capitalize()],
            name=entry["title"],
            fill="toself",
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
elif len(dimensions) < 3:
    chart_data = {}
    for entry in leaderboard:
        chart_data[entry["title"]] = entry["dimension_scores"]
    chart_df = pd.DataFrame(chart_data).T
    chart_df.columns = [d.capitalize() for d in chart_df.columns]
    st.bar_chart(chart_df)

st.divider()
st.subheader("Project Scores & Reasoning / 项目评分与推理")

project_names = {entry["project_id"]: entry["title"] for entry in leaderboard}
selected = st.selectbox("Select a project", options=list(project_names.keys()), format_func=lambda x: project_names[x])

if selected:
    entry = next(e for e in leaderboard if e["project_id"] == selected)
    st.markdown(f"### {entry['title']}")
    st.markdown(f"**Overall Weighted Score: {entry['weighted_score']:.2%}**")

    cols = st.columns(len(dimensions))
    for i, dim in enumerate(dimensions):
        score = entry["dimension_scores"].get(dim, 0)
        with cols[i]:
            st.metric(dim.capitalize(), f"{score:.2%}")

    try:
        from api_client import get_scores as fetch_scores
        all_scores = fetch_scores(entry["run_id"])
        project_scores = [s for s in all_scores if s["project_id"] == selected]

        if project_scores:
            for ps in project_scores:
                with st.expander(f"📝 {ps['dimension'].capitalize()} — Score: {ps['score']:.2%} (raw: {ps['raw_score']})"):
                    st.markdown(f"**Model:** `{ps.get('model_used', 'N/A')}`")
                    st.markdown("**Reasoning:**")
                    st.markdown(ps.get("reasoning", "No reasoning available."))
    except Exception:
        pass
