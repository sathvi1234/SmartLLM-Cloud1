from datetime import datetime, timedelta
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# OWASP recommends bcrypt with at least 10 rounds (passlib defaults to 12+)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(subject: Any, expires_delta: timedelta, token_type: str = "access") -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_access_token(subject: Any) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "access")

def create_refresh_token(subject: Any) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(subject, expires_delta, "refresh")

def create_verification_token(subject: Any) -> str:
    expires_delta = timedelta(minutes=settings.VERIFY_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "verify")

def create_reset_token(subject: Any) -> str:
    expires_delta = timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "reset")

def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
