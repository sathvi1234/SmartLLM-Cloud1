from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
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
    logger.info(f"Sending email to {email}\nSubject: {subject}\nBody: {body}")

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
