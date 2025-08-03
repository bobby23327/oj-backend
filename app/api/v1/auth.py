"""
认证相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.api.deps import get_current_user_id

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_session)
):
    """用户注册"""
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_session)
):
    """用户登录"""
    user_service = UserService(db)
    result = user_service.login_user(user_data)
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_session)
):
    """获取当前用户信息"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 