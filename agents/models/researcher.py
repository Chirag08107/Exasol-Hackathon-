from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    success: bool

    form_code: str

    requirements: List[Dict[str, Any]] = Field(default_factory=list)

    required_documents: List[Dict[str, Any]] = Field(default_factory=list)

    rules: List[Dict[str, Any]] = Field(default_factory=list)

    common_mistakes: List[Dict[str, Any]] = Field(default_factory=list)

    sources: List[Dict[str, Any]] = Field(default_factory=list)

    processing_information: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(default_factory=list)