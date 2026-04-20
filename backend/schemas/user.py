# schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr  # Pydantic will automatically validate that this is a real email format!
    unipd_id: Optional[str] = None

class UserCreate(UserBase):
    pass # No extra fields needed to create a user right now

class UserResponse(UserBase):
    id: int
    
    # This is the magic bridge! It tells Pydantic to read data directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
    
class UserCreate(UserBase):
    password: str # The raw password the student types in    