from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=64)

class VerifyEmail(BaseModel):
    token: str
