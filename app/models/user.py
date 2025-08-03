"""
用户数据模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    nickname: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    
    # 统计信息
    total_submissions: int = Field(default=0)
    accepted_submissions: int = Field(default=0)
    total_score: int = Field(default=0)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "nickname": "John Doe",
                "role": "user",
                "status": "active"
            }
        } 