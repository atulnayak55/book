from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MessageResponse(BaseModel):
    message: str


class SignupStartRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    unipd_id: str | None = Field(default=None, max_length=64)
    password: str = Field(min_length=8, max_length=128)


class SignupVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(pattern=r"^\d{6}$")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class VerificationTokenResponse(BaseModel):
    message: str
    expires_at: datetime
