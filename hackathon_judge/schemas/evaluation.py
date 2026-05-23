from datetime import datetime

from pydantic import BaseModel


class EvaluationRunOut(BaseModel):
    id: int
    hackathon_id: int
    status: str
    total_count: int
    completed_count: int
    started_at: datetime | None
    finished_at: datetime | None
    model_config = {"from_attributes": True}


class ProjectScoreOut(BaseModel):
    id: int
    evaluation_run_id: int
    project_id: int
    dimension: str
    score: float
    raw_score: float
    reasoning: str | None
    model_used: str | None
    tokens_used: int
    status: str
    model_config = {"from_attributes": True}


class HardRuleResultOut(BaseModel):
    id: int
    evaluation_run_id: int
    project_id: int
    hard_rule_id: int
    passed: bool
    detail: str | None
    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    project_id: int
    run_id: int
    title: str
    weighted_score: float
    dimension_scores: dict[str, float]
    hard_rules_passed: int
    hard_rules_total: int
