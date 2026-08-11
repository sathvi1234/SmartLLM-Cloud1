import os

files = {
    "backend/app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartLLM Cloud API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-for-development-only-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # Short lived access token (OWASP)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # Refresh token
    RESET_TOKEN_EXPIRE_MINUTES: int = 60 # Password reset token
    VERIFY_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # Email verification token
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smartllm"

    class Config:
        env_file = ".env"

settings = Settings()
""",
    "backend/app/core/security.py": """from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# OWASP recommends bcrypt with at least 10 rounds (passlib defaults to 12+)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(subject: str | any, expires_delta: timedelta, token_type: str = "access") -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_access_token(subject: str | any) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "access")

def create_refresh_token(subject: str | any) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(subject, expires_delta, "refresh")

def create_verification_token(subject: str | any) -> str:
    expires_delta = timedelta(minutes=settings.VERIFY_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "verify")

def create_reset_token(subject: str | any) -> str:
    expires_delta = timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "reset")

def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
""",
    "backend/app/models/user.py": """from sqlalchemy import Column, String, Boolean, DateTime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
""",
    "backend/app/schemas/user.py": """from pydantic import BaseModel, EmailStr, Field
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
""",
    "backend/app/schemas/token.py": """from pydantic import BaseModel, EmailStr, Field

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
""",
    "backend/app/api/dependencies.py": """from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == str(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    return current_user
""",
    "backend/app/api/v1/endpoints/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
import logging
from app.api.dependencies import get_db
from app.crud.user import get_user_by_email, create_user
from app.core.security import (
    verify_password, create_access_token, create_refresh_token,
    create_verification_token, create_reset_token, decode_token, get_password_hash
)
from app.schemas.token import Token, TokenRefresh, ForgotPassword, ResetPassword, VerifyEmail
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Mock email sender
def send_email(email: str, subject: str, body: str):
    logger.info(f"Sending email to {email}\\nSubject: {subject}\\nBody: {body}")

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=user_in.email)
    if user:
        # OWASP: Don't reveal if account exists, just return generic success or standard error.
        # But for UX, returning standard error on signup is common.
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = create_user(db, user_in)
    
    # Generate verification token and send email
    verify_token = create_verification_token(new_user.id)
    background_tasks.add_task(
        send_email,
        new_user.email,
        "Verify your email",
        f"Your verification token is: {verify_token}"
    )
    return new_user

@router.post("/verify-email")
def verify_email(payload: VerifyEmail, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(payload.token)
        if token_data.get("type") != "verify":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = token_data.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}
        
    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(db, email=form_data.username)
    # Generic error message to prevent email enumeration
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(payload: TokenRefresh, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = token_data.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
        
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer"
    }

@router.post("/forgot-password")
def forgot_password(payload: ForgotPassword, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=payload.email)
    if user and user.is_active:
        reset_token = create_reset_token(user.id)
        background_tasks.add_task(
            send_email,
            user.email,
            "Password Reset Request",
            f"Your password reset token is: {reset_token}"
        )
    # Always return success to prevent email enumeration (OWASP)
    return {"message": "If that email is registered, a password reset link has been sent."}

@router.post("/reset-password")
def reset_password(payload: ResetPassword, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(payload.token)
        if token_data.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = token_data.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")
        
    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password reset successfully"}
""",
    "backend/app/api/v1/endpoints/users.py": """from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user, get_current_verified_user
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/verified", response_model=UserResponse)
def read_user_me_verified(current_user: User = Depends(get_current_verified_user)):
    # This endpoint requires the user to be email verified
    return current_user
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Authentication implementation applied successfully.")
