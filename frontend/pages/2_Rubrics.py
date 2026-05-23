import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import (
    create_hard_rule,
    create_rubric,
    delete_hard_rule,
    delete_rubric,
    list_hackathons,
    list_hard_rules,
    list_rubrics,
    update_rubric,
)

st.set_page_config(page_title="Rubrics - Hackathon Auto Judge", layout="wide")
st.title("📋 Evaluation Rubrics")

st.info("""
**How evaluation works:** Each project is scored by an LLM across multiple **dimensions** (rubrics).
For each dimension, the system sends the project's description/README as **input** and the scraped
source code/file tree as **actual_output** to a [deepeval GEval](https://docs.confident-ai.com/docs/metrics-llm-evals)
metric. The LLM follows the **evaluation steps** you define below to produce a score (1-5) and reasoning.

**评审原理：** 每个项目按多个**维度**（评审标准）由 LLM 评分。系统将项目描述/README 作为输入，
抓取的源代码/文件树作为实际输出，发送给 deepeval GEval 指标。LLM 按照您定义的**评审步骤**
产生评分（1-5分）和推理说明。
""")

try:
    hackathons = list_hackathons()
except Exception as e:
    st.error(f"Cannot connect to backend: {e}")
    st.stop()

if not hackathons:
    st.warning("No hackathons found. The default one should be created on startup.")
    st.stop()

hid = hackathons[0]["id"]
rubrics = list_rubrics(hid)

DIMENSION_LABELS = {
    "technical": "Technical Soundness / 技术实力",
    "feature": "Feature Alignment / 功能对齐",
    "uiux": "UI/UX Innovation / 界面创新",
    "freshness": "Code Freshness / 代码新鲜度",
}

st.subheader("Evaluation Dimensions / 评审维度")

for rubric in rubrics:
    dim_label = DIMENSION_LABELS.get(rubric["dimension"], rubric["dimension"])
    with st.expander(f"**{rubric['name']}** ({dim_label}) — Weight: {rubric['weight']:.0%}", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input("Display Name", value=rubric["name"], key=f"name_{rubric['id']}")
            new_criteria = st.text_area(
                "Criteria (sent to LLM as evaluation criteria)",
                value=rubric["criteria"],
                key=f"criteria_{rubric['id']}",
                height=100,
                help="Describe what the LLM should evaluate. This becomes the GEval 'criteria' parameter.",
            )
            steps = rubric.get("evaluation_steps", [])
            new_steps_text = st.text_area(
                "Evaluation Steps (one per line — the LLM follows these step-by-step)",
                value="\n".join(steps),
                key=f"steps_{rubric['id']}",
                height=150,
                help="Each line is one evaluation step. The LLM processes them sequentially to arrive at a score.",
            )
        with col2:
            new_weight = st.slider(
                "Weight", 0.0, 1.0, rubric["weight"], 0.05,
                key=f"weight_{rubric['id']}",
                help="Relative weight in the final weighted score.",
            )
            is_active = st.checkbox("Active", value=rubric["is_active"], key=f"active_{rubric['id']}")

        bcol1, bcol2 = st.columns(2)
        with bcol1:
            if st.button("💾 Update", key=f"update_{rubric['id']}"):
                new_steps = [s.strip() for s in new_steps_text.strip().split("\n") if s.strip()]
                update_rubric(rubric["id"], {
                    "name": new_name,
                    "weight": new_weight,
                    "criteria": new_criteria,
                    "evaluation_steps": new_steps,
                    "is_active": is_active,
                })
                st.success("Updated!")
                st.rerun()
        with bcol2:
            if st.button("🗑️ Delete", key=f"delete_{rubric['id']}", type="secondary"):
                delete_rubric(rubric["id"])
                st.rerun()

st.divider()
st.subheader("Add Custom Dimension / 添加自定义维度")

with st.form("new_rubric"):
    new_dim = st.text_input("Dimension key", placeholder="e.g. innovation, creativity, security")
    new_rname = st.text_input("Display name", placeholder="e.g. Innovation Score")
    new_rweight = st.slider("Weight", 0.0, 1.0, 0.25, 0.05)
    new_rcriteria = st.text_area("Criteria", placeholder="Describe what this dimension evaluates...")
    new_rsteps = st.text_area("Evaluation Steps (one per line)", placeholder="Step 1: Check...\nStep 2: Assess...\nStep 3: Rate on 1-5 scale")
    if st.form_submit_button("➕ Add Dimension"):
        if new_dim and new_rname and new_rcriteria:
            steps = [s.strip() for s in new_rsteps.strip().split("\n") if s.strip()]
            create_rubric(hid, {
                "dimension": new_dim,
                "name": new_rname,
                "weight": new_rweight,
                "criteria": new_rcriteria,
                "evaluation_steps": steps,
            })
            st.success("Dimension added!")
            st.rerun()
        else:
            st.warning("Please fill in dimension key, name, and criteria.")

st.divider()
st.subheader("Hard Rules / 硬性规则")

st.info("""
Hard rules are **programmatic checks** (not LLM-based) that produce pass/fail results.
They run before LLM evaluation and appear alongside scores in the leaderboard.

硬性规则是**程序化检查**（非 LLM），产生通过/不通过结果，在排行榜中显示。

| Check Type | Description |
|------------|-------------|
| `readme_contains` | Check if README contains a specific keyword |
| `file_exists` | Check if a specific file exists in the repo |
| `commit_count_min` | Check if commit count meets a minimum threshold |
""")

hard_rules = list_hard_rules(hid)
if hard_rules:
    for rule in hard_rules:
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            st.markdown(f"**{rule['name']}**")
        with col2:
            st.code(f"{rule['check_type']} = {rule['check_value']}", language=None)
        with col3:
            if st.button("🗑️", key=f"rm_rule_{rule['id']}"):
                delete_hard_rule(rule["id"])
                st.rerun()
else:
    st.caption("No hard rules configured.")

with st.form("new_hard_rule"):
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        hr_name = st.text_input("Rule name", placeholder="e.g. Has README installation section")
    with col2:
        hr_type = st.selectbox("Check type", ["readme_contains", "file_exists", "commit_count_min"])
    with col3:
        hr_value = st.text_input("Check value", placeholder="e.g. installation, Dockerfile, 5")
    if st.form_submit_button("➕ Add Rule"):
        if hr_name and hr_value:
            create_hard_rule(hid, {"name": hr_name, "check_type": hr_type, "check_value": hr_value})
            st.success("Rule added!")
            st.rerun()
        else:
            st.warning("Please fill in rule name and check value.")
