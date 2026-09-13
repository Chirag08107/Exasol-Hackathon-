from pydantic import BaseModel

class FormResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    category: str | None = None
    official_url: str | None = None

class FormFieldResponse(BaseModel):
    id: int
    form_id: int
    field_code: str
    label: str
    field_type: str
    required: bool
    order: int