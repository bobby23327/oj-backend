"""
用户相关的API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.user_service import UserService
from app.schemas.user import UserUpdate, UserResponse
from app.api.deps import get_current_user_id, get_current_active_user_id

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    """获取用户列表"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_session)
):
    """获取用户信息"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """更新当前用户信息"""
    user_service = UserService(db)
    user = user_service.update_user(current_user_id, user_data)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """删除用户（仅管理员）"""
    # TODO: 添加管理员权限检查
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"} 