from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    firstName: str
    middleName: str | None = None
    lastName: str
    userName: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyRequest(BaseModel):
    phone: str
    otp: str
    address: str
    aadhaarNumber: str

class VerifyRequest(BaseModel):
    phone:str
    otp:str
    address:str
    aadhaarNumber:str

class GoogleLoginRequest(BaseModel):
    credential:str

class SendOtpRequest(BaseModel):
    phone:str

class VerifyOtpRequest(BaseModel):
    phone:str
    otp:str
    