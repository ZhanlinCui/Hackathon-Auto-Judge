from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="hackathon", cascade="all, delete-orphan")
    rubrics: Mapped[list["Rubric"]] = relationship(back_populates="hackathon", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    github_url: Mapped[str | None] = mapped_column(String(500))
    demo_url: Mapped[str | None] = mapped_column(String(500))
    pitch_text: Mapped[str | None] = mapped_column(Text)
    scrape_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    hackathon: Mapped["Hackathon"] = relationship(back_populates="projects")
    data: Mapped["ProjectData | None"] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    scores: Mapped[list["ProjectScore"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    hard_rule_results: Mapped[list["HardRuleResult"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectData(Base):
    __tablename__ = "project_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True, nullable=False)
    readme_content: Mapped[str | None] = mapped_column(Text)
    file_tree: Mapped[dict | None] = mapped_column(JSON)
    config_files: Mapped[dict | None] = mapped_column(JSON)
    source_files: Mapped[dict | None] = mapped_column(JSON)
    commit_summary: Mapped[dict | None] = mapped_column(JSON)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="data")


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    dimension: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=0.25)
    criteria: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_steps: Mapped[list] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    hackathon: Mapped["Hackathon"] = relationship(back_populates="rubrics")


class HardRule(Base):
    __tablename__ = "hard_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    check_type: Mapped[str] = mapped_column(String(50), nullable=False)
    check_value: Mapped[str] = mapped_column(String(500), nullable=False)

    results: Mapped[list["HardRuleResult"]] = relationship(back_populates="hard_rule", cascade="all, delete-orphan")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    model_config_snapshot: Mapped[dict | None] = mapped_column(JSON)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    scores: Mapped[list["ProjectScore"]] = relationship(back_populates="evaluation_run", cascade="all, delete-orphan")
    hard_rule_results: Mapped[list["HardRuleResult"]] = relationship(back_populates="evaluation_run", cascade="all, delete-orphan")


class ProjectScore(Base):
    __tablename__ = "project_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evaluation_run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    dimension: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    raw_score: Mapped[float] = mapped_column(Float, default=0.0)
    reasoning: Mapped[str | None] = mapped_column(Text)
    model_used: Mapped[str | None] = mapped_column(String(100))
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    evaluation_run: Mapped["EvaluationRun"] = relationship(back_populates="scores")
    project: Mapped["Project"] = relationship(back_populates="scores")


class HardRuleResult(Base):
    __tablename__ = "hard_rule_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evaluation_run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    hard_rule_id: Mapped[int] = mapped_column(ForeignKey("hard_rules.id"), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    detail: Mapped[str | None] = mapped_column(Text)

    evaluation_run: Mapped["EvaluationRun"] = relationship(back_populates="hard_rule_results")
    project: Mapped["Project"] = relationship(back_populates="hard_rule_results")
    hard_rule: Mapped["HardRule"] = relationship(back_populates="results")


class AppConfig(Base):
    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
