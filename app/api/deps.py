"""
依赖注入函数
"""
from typing import Generator
from sqlmodel import Session
from fastapi import Depends, HTTPException, status

from app.core.database import get_session
from app.core.security import get_current_user, get_current_active_user
from app.services.user_service import UserService


def get_user_service(db: Session = Depends(get_session)) -> UserService:
    """获取用户服务"""
    return UserService(db)


def get_current_user_id(current_user: dict = Depends(get_current_user)) -> int:
    """获取当前用户ID"""
    return int(current_user["user_id"])


def get_current_active_user_id(current_user: dict = Depends(get_current_active_user)) -> int:
    """获取当前活跃用户ID"""
    return int(current_user["user_id"]) 