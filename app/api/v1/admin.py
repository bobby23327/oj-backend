"""
管理相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.api.deps import get_current_active_user_id

router = APIRouter()


@router.get("/dashboard")
def get_admin_dashboard(
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """获取管理仪表板数据"""
    # TODO: 实现管理仪表板
    return {
        "total_users": 0,
        "total_problems": 0,
        "total_submissions": 0,
        "pending_judgments": 0
    }


@router.get("/system/status")
def get_system_status(
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """获取系统状态"""
    # TODO: 实现系统状态监控
    return {
        "database": "healthy",
        "redis": "healthy",
        "judge_service": "healthy",
        "celery": "healthy"
    }


@router.post("/system/restart-judge")
def restart_judge_service(
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """重启评测服务（仅管理员）"""
    # TODO: 实现重启评测服务
    return {"message": "Judge service restart requested"}


@router.get("/logs")
def get_system_logs(
    service: str = "all",
    lines: int = 100,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """获取系统日志（仅管理员）"""
    # TODO: 实现日志查看
    return {
        "logs": [],
        "service": service,
        "lines": lines
    } 