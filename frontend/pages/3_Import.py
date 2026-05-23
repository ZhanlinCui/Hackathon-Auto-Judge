import time

import pandas as pd
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import import_csv, list_hackathons, list_projects, scrape_all

st.set_page_config(page_title="Import - Hackathon Auto Judge", layout="wide")
st.title("📥 Import Projects")

try:
    hackathons = list_hackathons()
except Exception as e:
    st.error(f"Cannot connect to backend: {e}")
    st.stop()

if not hackathons:
    st.warning("No hackathons found.")
    st.stop()

hid = hackathons[0]["id"]

st.info("""
**CSV Format / CSV 格式说明:**

| Column | Required | Description |
|--------|----------|-------------|
| `title` | ✅ Yes | Project name |
| `description` | Optional | Short description of the project |
| `github_url` | Optional | GitHub repository URL (for code scraping) |
| `demo_url` | Optional | Demo or video link |
| `pitch_text` | Optional | Pitch or elevator description |
""")

col_upload, col_sample = st.columns([3, 1])

with col_upload:
    uploaded = st.file_uploader("Upload CSV file", type=["csv"])

with col_sample:
    st.markdown("")
    st.markdown("")
    sample_path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_projects.csv"
    if sample_path.exists():
        with open(sample_path, "rb") as f:
            st.download_button(
                "📄 Download Sample CSV",
                data=f.read(),
                file_name="sample_projects.csv",
                mime="text/csv",
            )

if uploaded:
    df = pd.read_csv(uploaded)
    st.subheader("Preview")
    st.dataframe(df, use_container_width=True)
    st.markdown(f"**{len(df)} projects** found in CSV")

    if st.button("📥 Import Projects", type="primary"):
        uploaded.seek(0)
        result = import_csv(hid, uploaded.read(), uploaded.name)
        st.success(f"Imported {len(result)} projects!")
        st.rerun()

st.divider()
st.subheader("Current Projects / 当前项目")

projects = list_projects(hid)
if projects:
    STATUS_COLORS = {
        "done": "🟢",
        "pending": "🟡",
        "scraping": "🔵",
        "error": "🔴",
        "no_repo": "⚪",
    }

    rows = []
    for p in projects:
        status_icon = STATUS_COLORS.get(p["scrape_status"], "⚪")
        rows.append({
            "ID": p["id"],
            "Title": p["title"],
            "GitHub URL": p.get("github_url") or "—",
            "Status": f"{status_icon} {p['scrape_status']}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    pending = [p for p in projects if p["scrape_status"] in ("pending", "error")]
    if pending:
        if st.button(f"🔗 Scrape {len(pending)} Projects", type="primary"):
            scrape_all(hid)
            st.info("Scraping started in background...")

            progress = st.progress(0)
            for i in range(20):
                time.sleep(3)
                updated = list_projects(hid)
                done = sum(1 for p in updated if p["scrape_status"] == "done")
                total = len(updated)
                progress.progress(done / total if total else 0)
                if all(p["scrape_status"] not in ("pending", "scraping") for p in updated):
                    break
            st.rerun()
    else:
        scraped = sum(1 for p in projects if p["scrape_status"] == "done")
        errors = sum(1 for p in projects if p["scrape_status"] == "error")
        msg = f"All projects processed. {scraped}/{len(projects)} scraped successfully."
        if errors:
            msg += f" {errors} failed."
        st.info(msg)
else:
    st.caption("No projects imported yet. Upload a CSV above.")
