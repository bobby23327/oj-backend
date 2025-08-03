"""
提交相关的Pydantic模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.submission import SubmissionStatus, ProgrammingLanguage


class SubmissionBase(BaseModel):
    """提交基础模式"""
    code: str
    language: ProgrammingLanguage


class SubmissionCreate(SubmissionBase):
    """提交创建模式"""
    problem_id: int


class SubmissionResponse(SubmissionBase):
    """提交响应模式"""
    id: int
    user_id: int
    problem_id: int
    status: SubmissionStatus
    score: Optional[int] = None
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    error_message: Optional[str] = None
    compile_error: Optional[str] = None
    passed_tests: Optional[int] = None
    total_tests: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    judged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubmissionList(BaseModel):
    """提交列表模式"""
    id: int
    problem_id: int
    language: ProgrammingLanguage
    status: SubmissionStatus
    score: Optional[int] = None
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionStatus(BaseModel):
    """提交状态模式"""
    id: int
    status: SubmissionStatus
    score: Optional[int] = None
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    error_message: Optional[str] = None
    compile_error: Optional[str] = None
    passed_tests: Optional[int] = None
    total_tests: Optional[int] = None
    judged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JudgeResult(BaseModel):
    """评测结果模式"""
    submission_id: int
    status: SubmissionStatus
    score: Optional[int] = None
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    error_message: Optional[str] = None
    compile_error: Optional[str] = None
    passed_tests: Optional[int] = None
    total_tests: Optional[int] = None
    test_results: Optional[list] = None 