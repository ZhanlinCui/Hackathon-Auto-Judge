<p align="center">
  <h1 align="center">⚖️ Hackathon Judge</h1>
  <p align="center">
    <strong>AI-powered evaluation platform for hackathon projects</strong>
  </p>
  <p align="center">
    Import projects. Scrape repos. Let LLMs score them. Get a leaderboard.
  </p>
  <p align="center">
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
    <a href="https://github.com/ZhanlinCui/Hackathon-Judge/stargazers"><img src="https://img.shields.io/github/stars/ZhanlinCui/Hackathon-Judge?style=social" alt="GitHub Stars"></a>
    <a href="https://github.com/ZhanlinCui/Hackathon-Judge/issues"><img src="https://img.shields.io/github/issues/ZhanlinCui/Hackathon-Judge" alt="Issues"></a>
  </p>
  <p align="center">
    <a href="README_CN.md">🇨🇳 中文</a> · <a href="#-quick-start">Quick Start</a> · <a href="http://127.0.0.1:8000/docs">API Docs</a>
  </p>
</p>

---

## 🤔 Why Hackathon Judge?

Judging hackathon projects is **painful**. Dozens of repos, inconsistent pitches, subjective scoring — it doesn't scale.

**Hackathon Judge automates this.** It scrapes each project's GitHub repo, feeds the code to an LLM through [deepeval](https://github.com/confident-ai/deepeval) GEval metrics, and produces **structured, explainable scores** across multiple dimensions — with full reasoning for every score.

> **For hackathon organizers** who want fair, consistent, and scalable evaluation.
> **For developers** who want transparent feedback on their projects.

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### 🔬 LLM Evaluation
Score projects across customizable dimensions using any LLM. Built on deepeval GEval — the same framework used for LLM testing in production.

</td>
<td width="33%" valign="top">

### 🔗 GitHub Scraping
Auto-fetches README, file tree, source code, config files, and commit history. Smart file selection prioritizes `src/`, `app/`, `lib/` directories.

</td>
<td width="33%" valign="top">

### 📊 Multi-Dimension
4 built-in dimensions: Technical Soundness, Feature Alignment, UI/UX Innovation, Code Freshness. Add your own or customize everything.

</td>
</tr>
<tr>
<td width="33%" valign="top">

### 🏆 Interactive Leaderboard
Weighted scores, radar charts, conditional coloring, per-dimension sorting. Export to Excel with one click.

</td>
<td width="33%" valign="top">

### 🧠 Explainable Scores
Every score comes with full LLM reasoning. Understand *why* a project scored high or low on each dimension.

</td>
<td width="33%" valign="top">

### 🌐 Multi-Provider LLM
OpenAI, Anthropic, Google Gemini, DeepSeek — or any of 100+ providers via [LiteLLM](https://github.com/BerriAI/litellm). Mix models per dimension.

</td>
</tr>
</table>

---

## ⚙️ How It Works

```mermaid
graph LR
    A["📄 CSV Import"] --> B["🔗 GitHub Scraper"]
    B --> C["📏 Token Budget"]
    C --> D["🤖 LLM + GEval"]
    D --> E["🏆 Leaderboard"]
    
    style A fill:#4CAF50,stroke:#333,color:#fff
    style B fill:#2196F3,stroke:#333,color:#fff
    style C fill:#FF9800,stroke:#333,color:#fff
    style D fill:#9C27B0,stroke:#333,color:#fff
    style E fill:#F44336,stroke:#333,color:#fff
```

| Step | What Happens |
|------|-------------|
| **1. Import** | Upload a CSV with project info (title, GitHub URL, description) |
| **2. Scrape** | System fetches README, source code, configs, and commits via GitHub API |
| **3. Evaluate** | Each project is scored by an LLM across your configured dimensions using [deepeval GEval](https://docs.confident-ai.com/docs/metrics-llm-evals) |
| **4. Review** | View ranked leaderboard, read per-score reasoning, export to Excel |

---

## 🚀 Quick Start

**1. Install**

```bash
git clone https://github.com/ZhanlinCui/Hackathon-Judge.git
cd Hackathon-Judge
pip install -e .
```

**2. Configure**

```bash
cp .env.example .env
# Add at least one LLM API key (OpenAI, Gemini, Anthropic, or DeepSeek)
# Add a GitHub token for repo scraping (optional but recommended)
```

**3. Run**

```bash
./start.sh
# API  → http://127.0.0.1:8000  (Swagger docs at /docs)
# UI   → http://127.0.0.1:8501
```

That's it. Open the UI, configure your API key, import a CSV, and run evaluation.

---

## 📋 Evaluation Dimensions

4 dimensions ship by default. All are fully customizable — edit criteria, evaluation steps, weights, or add entirely new ones.

<details>
<summary><strong>🔧 Technical Soundness</strong> — 30% weight</summary>

**Criteria:** Evaluate code architecture, technology choices, error handling, code organization, and engineering best practices.

**Evaluation Steps:**
1. Review the project's file structure and code organization
2. Examine the choice of technologies and frameworks
3. Look at source code quality — naming, modularity, separation of concerns
4. Check configuration files — are dependencies reasonable?
5. Assess commit history — iterative development and meaningful progress?
6. Rate overall technical soundness on a scale of 1-5
</details>

<details>
<summary><strong>🎯 Feature Alignment</strong> — 25% weight</summary>

**Criteria:** Compare the project description and pitch with what the code actually implements. Consider feature completeness, functionality depth, and whether the demo matches the promise.

**Evaluation Steps:**
1. Read the project description/pitch and identify key features promised
2. Examine the codebase to verify which features are actually implemented
3. Assess the depth of each feature — stub or working implementation?
4. Check if the README documents how to use the features
5. Consider whether scope is appropriate for a hackathon timeframe
6. Rate feature alignment on a scale of 1-5
</details>

<details>
<summary><strong>🎨 UI/UX Innovation</strong> — 20% weight</summary>

**Criteria:** Evaluate design quality, usability, accessibility, innovative interaction patterns, and overall polish of frontend or user-facing components.

**Evaluation Steps:**
1. Look at frontend code for design quality
2. Assess navigation flow and information architecture
3. Check for responsive design, accessibility, and error states
4. Evaluate innovative or creative UI/UX patterns
5. Consider overall user experience implied by code and README
6. Rate UI/UX innovation on a scale of 1-5
</details>

<details>
<summary><strong>🆕 Code Freshness</strong> — 25% weight</summary>

**Criteria:** Evaluate whether this project was genuinely built during the hackathon vs. pre-existing code being repurposed. Consider commit patterns, code consistency, and cohesiveness.

**Evaluation Steps:**
1. Analyze commit history — are commits spread over the hackathon period?
2. Check for scaffolding commits followed by feature development
3. Look for code style consistency
4. Check for standard boilerplate (OK) vs. pre-built features (not OK)
5. Assess whether complexity matches what could reasonably be built in a hackathon
6. Rate code freshness on a scale of 1-5
</details>

---

## 🌐 Supported LLM Providers

Any model supported by [LiteLLM](https://docs.litellm.ai/docs/providers) works out of the box.

| Provider | Model Examples | Env Variable |
|----------|---------------|-------------|
| **OpenAI** | `gpt-4o`, `gpt-4o-mini` | `OPENAI_API_KEY` |
| **Google Gemini** | `gemini/gemini-2.5-flash`, `gemini/gemini-2.5-pro` | `GEMINI_API_KEY` |
| **Anthropic** | `anthropic/claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| **DeepSeek** | `deepseek/deepseek-chat` | `DEEPSEEK_API_KEY` |
| **100+ more** | See [LiteLLM docs](https://docs.litellm.ai/docs/providers) | Various |

> **Pro tip:** You can assign different models to different dimensions. Use a cheaper model for straightforward checks and a stronger model for nuanced evaluation.

---

## 📄 CSV Format

| Column | Required | Description |
|--------|:--------:|-------------|
| `title` | ✅ | Project name |
| `description` | | Short description of the project |
| `github_url` | | GitHub repository URL (for code scraping) |
| `demo_url` | | Demo or video link |
| `pitch_text` | | Pitch / elevator description |

> A sample CSV is included at [`data/sample_projects.csv`](data/sample_projects.csv).

---

## 🏗️ Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) | REST API with auto-generated docs |
| Frontend | [Streamlit](https://streamlit.io/) | Interactive UI with charts |
| Database | [SQLite](https://www.sqlite.org/) + [aiosqlite](https://github.com/omnilib/aiosqlite) | Async persistence, zero setup |
| LLM Gateway | [LiteLLM](https://github.com/BerriAI/litellm) | Unified interface for 100+ LLM providers |
| Evaluation | [deepeval](https://github.com/confident-ai/deepeval) | GEval metrics with structured scoring |
| GitHub | [PyGithub](https://github.com/PyGithub/PyGithub) | Repo scraping via Trees API |
| Charts | [Plotly](https://plotly.com/python/) | Radar charts & visualizations |

---

<details>
<summary><strong>📡 API Endpoints (20 endpoints)</strong></summary>

Full interactive docs available at `http://127.0.0.1:8000/docs` when the server is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/hackathons` | Create a hackathon |
| `GET` | `/api/hackathons` | List all hackathons |
| `GET` | `/api/hackathons/{id}` | Get hackathon details |
| `POST` | `/api/hackathons/{id}/import` | Import projects from CSV |
| `GET` | `/api/hackathons/{id}/projects` | List projects |
| `POST` | `/api/hackathons/{id}/scrape` | Scrape all pending repos |
| `GET` | `/api/projects/{id}` | Get project details |
| `GET` | `/api/projects/{id}/data` | Get scraped project data |
| `GET` | `/api/hackathons/{id}/rubrics` | List evaluation rubrics |
| `POST` | `/api/hackathons/{id}/rubrics` | Create a rubric |
| `PUT` | `/api/rubrics/{id}` | Update a rubric |
| `DELETE` | `/api/rubrics/{id}` | Delete a rubric |
| `GET` | `/api/hackathons/{id}/hard-rules` | List hard rules |
| `POST` | `/api/hackathons/{id}/hard-rules` | Create a hard rule |
| `DELETE` | `/api/hard-rules/{id}` | Delete a hard rule |
| `POST` | `/api/hackathons/{id}/evaluate` | Start evaluation run |
| `GET` | `/api/evaluation-runs/{id}` | Get evaluation status |
| `GET` | `/api/evaluation-runs/{id}/scores` | Get all scores |
| `GET` | `/api/hackathons/{id}/leaderboard` | Get ranked leaderboard |
| `GET` | `/api/hackathons/{id}/export` | Download Excel report |

</details>

<details>
<summary><strong>📁 Project Structure</strong></summary>

```
Hackathon-Judge/
├── hackathon_judge/              # Backend package
│   ├── main.py                   # FastAPI app + startup
│   ├── config/settings.py        # Pydantic Settings + AppConfig helpers
│   ├── db/
│   │   ├── engine.py             # Async SQLAlchemy engine
│   │   └── models.py             # 8 ORM models
│   ├── schemas/                  # Pydantic request/response models
│   ├── api/                      # 5 route modules
│   ├── services/
│   │   ├── github_scraper.py     # GitHub API scraping
│   │   ├── token_budget.py       # tiktoken-based budget control
│   │   ├── evaluation_engine.py  # deepeval GEval orchestration
│   │   ├── llm_provider.py       # LiteLLM model factory
│   │   └── ingestion.py          # CSV parsing + import
│   └── rubrics/defaults.py       # 4 default dimension definitions
├── frontend/
│   ├── app.py                    # Streamlit home page
│   ├── api_client.py             # Backend API client
│   └── pages/                    # 6 Streamlit pages
├── data/sample_projects.csv
├── start.sh                      # One-command launcher
├── pyproject.toml
└── .env.example
```

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how:

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/Hackathon-Judge.git
cd Hackathon-Judge

# 2. Install in dev mode
pip install -e .

# 3. Create a branch
git checkout -b feature/your-feature

# 4. Make changes, then submit a PR
```

**Ideas for contribution:**
- Additional evaluation dimensions
- New hard rule check types
- Docker support
- More LLM provider integrations
- UI/UX improvements
- Documentation and translations

---

## 📜 License

[MIT](LICENSE) — use it however you want.

---

<p align="center">
  <sub>Built with ❤️ for the hackathon community</sub>
</p>
