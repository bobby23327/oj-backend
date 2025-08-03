"""
排行榜相关的API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.rank import UserRankList, RankFilter
from app.api.deps import get_current_active_user_id

router = APIRouter()


@router.get("/", response_model=List[UserRankList])
def get_rankings(
    page: int = 1,
    size: int = 20,
    time_range: str = "all",
    db: Session = Depends(get_session)
):
    """获取用户排行榜"""
    # TODO: 实现排行榜服务
    return []


@router.get("/user/{user_id}")
def get_user_rank(
    user_id: int,
    db: Session = Depends(get_session)
):
    """获取用户排名信息"""
    # TODO: 实现用户排名查询
    return {
        "user_id": user_id,
        "rank": 0,
        "total_score": 0,
        "solved_problems": 0
    }


@router.get("/me")
def get_my_rank(
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """获取我的排名信息"""
    # TODO: 实现我的排名查询
    return {
        "user_id": current_user_id,
        "rank": 0,
        "total_score": 0,
        "solved_problems": 0
    } 