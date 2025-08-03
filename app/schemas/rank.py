"""
排行榜相关的Pydantic模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserRankResponse(BaseModel):
    """用户排行榜响应模式"""
    id: int
    user_id: int
    rank: int
    total_score: int
    solved_problems: int
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    average_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserRankList(BaseModel):
    """用户排行榜列表模式"""
    rank: int
    user_id: int
    username: str
    nickname: Optional[str] = None
    total_score: int
    solved_problems: int
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    
    class Config:
        from_attributes = True


class RankFilter(BaseModel):
    """排行榜过滤模式"""
    page: int = 1
    size: int = 20
    time_range: Optional[str] = None  # "week", "month", "year", "all" 