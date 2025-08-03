"""
题目相关的API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.problem import ProblemCreate, ProblemUpdate, ProblemResponse, ProblemList, TestCaseCreate, TestCaseResponse
from app.api.deps import get_current_active_user_id

router = APIRouter()


@router.get("/", response_model=List[ProblemList])
def get_problems(
    skip: int = 0,
    limit: int = 100,
    difficulty: str = None,
    status: str = None,
    db: Session = Depends(get_session)
):
    """获取题目列表"""
    # TODO: 实现题目服务
    return []


@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(
    problem_id: int,
    db: Session = Depends(get_session)
):
    """获取题目详情"""
    # TODO: 实现题目服务
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Problem not found"
    )


@router.post("/", response_model=ProblemResponse)
def create_problem(
    problem_data: ProblemCreate,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """创建题目（仅管理员）"""
    # TODO: 实现题目服务
    return {}


@router.put("/{problem_id}", response_model=ProblemResponse)
def update_problem(
    problem_id: int,
    problem_data: ProblemUpdate,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """更新题目（仅管理员）"""
    # TODO: 实现题目服务
    return {}


@router.delete("/{problem_id}")
def delete_problem(
    problem_id: int,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """删除题目（仅管理员）"""
    # TODO: 实现题目服务
    return {"message": "Problem deleted successfully"}


@router.post("/{problem_id}/test-cases", response_model=TestCaseResponse)
def create_test_case(
    problem_id: int,
    test_case_data: TestCaseCreate,
    current_user_id: int = Depends(get_current_active_user_id),
    db: Session = Depends(get_session)
):
    """创建测试用例（仅管理员）"""
    # TODO: 实现测试用例服务
    return {} 