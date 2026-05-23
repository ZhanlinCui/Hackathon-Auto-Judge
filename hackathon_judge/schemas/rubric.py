from pydantic import BaseModel


class RubricCreate(BaseModel):
    dimension: str
    name: str
    weight: float = 0.25
    criteria: str
    evaluation_steps: list[str]
    is_active: bool = True


class RubricUpdate(BaseModel):
    name: str | None = None
    weight: float | None = None
    criteria: str | None = None
    evaluation_steps: list[str] | None = None
    is_active: bool | None = None


class RubricOut(BaseModel):
    id: int
    hackathon_id: int
    dimension: str
    name: str
    weight: float
    criteria: str
    evaluation_steps: list
    is_active: bool
    model_config = {"from_attributes": True}


class HardRuleCreate(BaseModel):
    name: str
    check_type: str
    check_value: str


class HardRuleOut(BaseModel):
    id: int
    hackathon_id: int
    name: str
    check_type: str
    check_value: str
    model_config = {"from_attributes": True}
