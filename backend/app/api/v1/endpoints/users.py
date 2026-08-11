from fastapi import APIRouter, Depends
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
