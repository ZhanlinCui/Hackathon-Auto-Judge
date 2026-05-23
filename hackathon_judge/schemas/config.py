from pydantic import BaseModel


class ConfigUpdate(BaseModel):
    key: str
    value: str


class ConfigOut(BaseModel):
    configs: dict[str, str]
