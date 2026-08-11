from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    # OWASP: Password complexity (min 8 chars, max 64)
    password: str = Field(..., min_length=8, max_length=64)

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
