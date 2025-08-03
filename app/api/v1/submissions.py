"""
提交相关的API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.submission import SubmissionCreate, SubmissionResponse, SubmissionList
from app.api.deps import get_current_active_user_id

router = APIRouter()


@router.post("/", response_model=SubmissionResponse)
def create_submission(
    submission_data: SubmissionCreate,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """创建代码提交"""
    # TODO: 实现提交服务
    return {}


@router.get("/", response_model=List[SubmissionList])
def get_submissions(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    problem_id: int = None,
    status: str = None,
    db: Session = Depends(get_session)
):
    """获取提交列表"""
    # TODO: 实现提交服务
    return []


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_session)
):
    """获取提交详情"""
    # TODO: 实现提交服务
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Submission not found"
    )


@router.get("/me", response_model=List[SubmissionList])
def get_my_submissions(
    skip: int = 0,
    limit: int = 100,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """获取我的提交列表"""
    # TODO: 实现提交服务
    return [] 