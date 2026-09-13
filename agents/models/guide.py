from typing import Any, Dict, List

from pydantic import BaseModel, Field


class GuideQuestion(BaseModel):
    field_code: str
    question: str
    reason: str


class GuideAction(BaseModel):
    field_code: str
    action: str
    value: Any = None
    source: str = "unknown"


class GuideResult(BaseModel):
    success: bool

    questions: List[GuideQuestion] = Field(default_factory=list)

    actions: List[GuideAction] = Field(default_factory=list)

    feedback: List[str] = Field(default_factory=list)

    next_field: str | None = None

    progress: str = ""