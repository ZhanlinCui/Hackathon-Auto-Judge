from pydantic import BaseModel


class HackathonCreate(BaseModel):
    name: str
    description: str | None = None


class HackathonOut(BaseModel):
    id: int
    name: str
    description: str | None
    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: int
    hackathon_id: int
    title: str
    description: str | None
    github_url: str | None
    demo_url: str | None
    pitch_text: str | None
    scrape_status: str
    model_config = {"from_attributes": True}


class ProjectDataOut(BaseModel):
    id: int
    project_id: int
    readme_content: str | None
    file_tree: dict | str | None
    config_files: dict | None
    source_files: dict | None
    commit_summary: list | dict | None
    total_tokens: int
    model_config = {"from_attributes": True}
