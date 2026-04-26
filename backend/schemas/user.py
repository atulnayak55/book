# schemas/user.py
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublicResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    unipd_id: Optional[str] = None
    password: str


class UserProfileResponse(UserPublicResponse):
    email: EmailStr
    unipd_id: Optional[str] = None
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)
