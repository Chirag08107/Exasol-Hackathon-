from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FormInfo(BaseModel):
    form_id: Optional[int] = None
    form_code: str
    form_name: str
    category: Optional[str] = None
    authority: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None


class FormField(BaseModel):
    field_id: Optional[int] = None
    field_code: str
    field_label: str
    field_type: Optional[str] = None
    section_name: Optional[str] = None
    is_required: bool = False
    field_order: Optional[int] = None
    explanation: Optional[str] = None
    example_value: Optional[str] = None
    validation_pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


class UserProfile(BaseModel):
    user_id: Optional[str] = None

    personal_information: Dict[str, Any] = Field(default_factory=dict)
    education: Dict[str, Any] = Field(default_factory=dict)
    additional_details: Dict[str, Any] = Field(default_factory=dict)


class AgentIssue(BaseModel):
    field: Optional[str] = None
    issue: str
    severity: str = "MEDIUM"


class ChecklistItem(BaseModel):
    item: str
    completed: bool = False


class FormSession(BaseModel):
    form: Optional[FormInfo] = None
    fields: List[FormField] = Field(default_factory=list)
    profile: Optional[UserProfile] = None
    answers: Dict[str, Any] = Field(default_factory=dict)
    research: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)