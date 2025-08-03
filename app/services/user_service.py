"""
用户服务类
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = self.db.exec(
            select(User).where(User.username == user_data.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 检查邮箱是否已存在
        existing_email = self.db.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            nickname=user_data.nickname,
            hashed_password=hashed_password,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = self.db.exec(
            select(User).where(User.username == username)
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is not active"
            )
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def login_user(self, user_data: UserLogin) -> dict:
        """用户登录"""
        user = self.authenticate_user(user_data.username, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.exec(select(User).where(User.id == user_id)).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.exec(select(User).where(User.username == username)).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 更新字段
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return self.db.exec(select(User).offset(skip).limit(limit)).all()
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def update_user_stats(self, user_id: int, submission_accepted: bool = False):
        """更新用户统计信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return
        
        user.total_submissions += 1
        if submission_accepted:
            user.accepted_submissions += 1
        
        # 计算通过率
        if user.total_submissions > 0:
            user.acceptance_rate = user.accepted_submissions / user.total_submissions
        
        user.updated_at = datetime.utcnow()
        self.db.commit() 