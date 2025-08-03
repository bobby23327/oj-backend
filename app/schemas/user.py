"""
用户相关的Pydantic模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模式"""
    password: str


class UserUpdate(BaseModel):
    """用户更新模式"""
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str
    password: str


class Token(BaseModel):
    """令牌模式"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模式"""
    username: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    role: UserRole
    status: UserStatus
    total_submissions: int
    accepted_submissions: int
    total_score: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户资料模式"""
    id: int
    username: str
    nickname: Optional[str] = None
    role: UserRole
    total_submissions: int
    accepted_submissions: int
    total_score: int
    acceptance_rate: float
    
    class Config:
        from_attributes = True 