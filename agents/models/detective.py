from typing import List

from pydantic import BaseModel, Field

from .common import FormField, FormInfo


class DetectiveResult(BaseModel):
    success: bool
    form: FormInfo | None = None

    confidence: float = 0.0

    source: str = "pdf"

    extracted_text: str = ""

    fields: List[FormField] = Field(default_factory=list)

    warnings: List[str] = Field(default_factory=list)