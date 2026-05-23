import asyncio
import logging
import re
from pathlib import PurePosixPath

from github import Github, GithubException

from hackathon_judge.services.token_budget import TokenBudget

logger = logging.getLogger(__name__)

SKIP_DIRS = {
    "node_modules", "dist", "build", ".git", "__pycache__", ".next",
    "vendor", ".venv", "venv", "env", ".tox", "eggs", ".eggs",
    "bower_components", "jspm_packages", ".cache", "coverage",
}

PRIORITY_DIRS = {
    "src", "app", "lib", "agents", "controllers", "models",
    "services", "handlers", "core", "api", "views", "components",
}

CONFIG_PATTERNS = {
    "package.json", "requirements.txt", "pyproject.toml", "setup.py",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "tsconfig.json", "vite.config.ts", "vite.config.js",
}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".kt", ".swift", ".rb", ".php", ".cs", ".cpp", ".c", ".vue", ".svelte",
}


def _parse_github_url(url: str) -> tuple[str, str] | None:
    patterns = [
        r"github\.com/([^/]+)/([^/\s?#]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            owner, repo = m.group(1), m.group(2)
            repo = repo.removesuffix(".git")
            return owner, repo
    return None


def _should_skip(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return any(p in SKIP_DIRS for p in parts)


def _is_config_file(path: str) -> bool:
    return PurePosixPath(path).name in CONFIG_PATTERNS


def _is_source_file(path: str) -> bool:
    return PurePosixPath(path).suffix in SOURCE_EXTENSIONS


def _priority_score(path: str) -> int:
    parts = set(PurePosixPath(path).parts)
    score = len(parts & PRIORITY_DIRS) * 10
    depth = len(PurePosixPath(path).parts)
    score -= depth
    return score


def scrape_repo(github_url: str, token: str, budget: int = 30000) -> dict:
    parsed = _parse_github_url(github_url)
    if not parsed:
        raise ValueError(f"Cannot parse GitHub URL: {github_url}")

    owner, repo_name = parsed
    g = Github(token) if token else Github()

    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
    except GithubException as e:
        raise ValueError(f"Cannot access repo {owner}/{repo_name}: {e}") from e

    readme_content = ""
    try:
        readme = repo.get_readme()
        readme_content = readme.decoded_content.decode("utf-8", errors="replace")
    except GithubException:
        pass

    try:
        tree = repo.get_git_tree(repo.default_branch, recursive=True)
        all_paths = [item.path for item in tree.tree if item.type == "blob"]
    except GithubException:
        all_paths = []

    file_tree_str = "\n".join(p for p in all_paths if not _should_skip(p))

    config_files = {}
    source_files = {}

    valid_paths = [p for p in all_paths if not _should_skip(p)]

    config_paths = [p for p in valid_paths if _is_config_file(p)]
    source_paths = [p for p in valid_paths if _is_source_file(p)]
    source_paths.sort(key=_priority_score, reverse=True)

    for path in config_paths[:10]:
        try:
            content = repo.get_contents(path)
            if content.size and content.size < 50000:
                config_files[path] = content.decoded_content.decode("utf-8", errors="replace")
        except GithubException:
            continue

    for path in source_paths[:30]:
        try:
            content = repo.get_contents(path)
            if content.size and content.size < 50000:
                source_files[path] = content.decoded_content.decode("utf-8", errors="replace")
        except GithubException:
            continue

    commits_data = []
    try:
        commits = repo.get_commits()
        for c in list(commits[:20]):
            commits_data.append({
                "sha": c.sha[:7],
                "message": c.commit.message.split("\n")[0][:100],
                "author": c.commit.author.name if c.commit.author else "unknown",
                "date": c.commit.author.date.isoformat() if c.commit.author and c.commit.author.date else "",
            })
    except GithubException:
        pass

    tb = TokenBudget(budget)
    allocated = tb.allocate(readme_content, file_tree_str, config_files, source_files)

    return {
        "readme_content": allocated["readme"],
        "file_tree": file_tree_str,
        "config_files": allocated["config_files"],
        "source_files": allocated["source_files"],
        "commit_summary": commits_data,
        "total_tokens": allocated["total_tokens"],
    }


async def scrape_repo_async(github_url: str, token: str, budget: int = 30000) -> dict:
    return await asyncio.to_thread(scrape_repo, github_url, token, budget)
