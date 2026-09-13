from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    form_id: int


class AnswerRequest(BaseModel):
    field_id: int
    value: str


class SessionResponse(BaseModel):
    session_id: int
    form_id: int
    status: str

class SessionDetailResponse(BaseModel):
    session_id: int
    form_id: int
    status:str
    current_field: dict | None
    progress: dict
    