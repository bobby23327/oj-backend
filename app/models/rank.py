"""
排行榜数据模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class UserRank(SQLModel, table=True):
    """用户排行榜模型"""
    __tablename__ = "user_ranks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    
    # 排名信息
    rank: int = Field(default=0)
    total_score: int = Field(default=0)
    solved_problems: int = Field(default=0)
    total_submissions: int = Field(default=0)
    accepted_submissions: int = Field(default=0)
    
    # 统计信息
    acceptance_rate: float = Field(default=0.0)
    average_time: Optional[float] = Field(default=None)  # 平均解题时间(小时)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "total_score": 1500,
                "solved_problems": 50,
                "total_submissions": 200,
                "accepted_submissions": 150,
                "acceptance_rate": 0.75
            }
        } 