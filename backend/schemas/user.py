from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    firstName: str
    middleName: str | None = None
    lastName: str
    userName: str
    email: EmailStr
    verified: bool


class UpdateProfileRequest(BaseModel):
    firstName: str
    middleName: str | None = None
    lastName: str
    address: str | None = None