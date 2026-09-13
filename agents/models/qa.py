from typing import Any, Dict, List

from pydantic import BaseModel, Field


class QAResult(BaseModel):
    valid: bool

    risk_level: str = "LOW"

    blocking_issues: List[Dict[str, Any]] = Field(default_factory=list)

    warnings: List[Dict[str, Any]] = Field(default_factory=list)

    checklist: List[str] = Field(default_factory=list)

    ready_for_review: bool = False