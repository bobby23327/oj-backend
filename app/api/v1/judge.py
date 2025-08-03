"""
评测相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.api.deps import get_current_active_user_id

router = APIRouter()


@router.get("/status/{submission_id}")
def get_judge_status(
    submission_id: int,
    db: Session = Depends(get_session)
):
    """获取评测状态"""
    # TODO: 实现评测状态查询
    return {
        "submission_id": submission_id,
        "status": "pending",
        "progress": 0
    }


@router.post("/{submission_id}/rejudge")
def rejudge_submission(
    submission_id: int,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """重新评测提交（仅管理员）"""
    # TODO: 实现重新评测
    return {"message": "Rejudge request submitted"}


@router.get("/queue")
def get_judge_queue(
    db: Session = Depends(get_session)
):
    """获取评测队列状态（仅管理员）"""
    # TODO: 实现队列状态查询
    return {
        "pending": 0,
        "judging": 0,
        "total": 0
    } 