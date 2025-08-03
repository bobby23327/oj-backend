"""
题目相关的Pydantic模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.problem import ProblemDifficulty, ProblemStatus


class ProblemBase(BaseModel):
    """题目基础模式"""
    title: str
    description: str
    difficulty: ProblemDifficulty
    time_limit: int
    memory_limit: int
    output_limit: int


class ProblemCreate(ProblemBase):
    """题目创建模式"""
    pass


class ProblemUpdate(BaseModel):
    """题目更新模式"""
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[ProblemDifficulty] = None
    status: Optional[ProblemStatus] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    output_limit: Optional[int] = None


class ProblemResponse(ProblemBase):
    """题目响应模式"""
    id: int
    status: ProblemStatus
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    created_by: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProblemList(BaseModel):
    """题目列表模式"""
    id: int
    title: str
    difficulty: ProblemDifficulty
    status: ProblemStatus
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    
    class Config:
        from_attributes = True


class TestCaseBase(BaseModel):
    """测试用例基础模式"""
    name: str
    input_data: str
    expected_output: str
    is_sample: bool = False
    is_hidden: bool = False


class TestCaseCreate(TestCaseBase):
    """测试用例创建模式"""
    problem_id: int


class TestCaseUpdate(BaseModel):
    """测试用例更新模式"""
    name: Optional[str] = None
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    is_sample: Optional[bool] = None
    is_hidden: Optional[bool] = None


class TestCaseResponse(TestCaseBase):
    """测试用例响应模式"""
    id: int
    problem_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProblemDetail(ProblemResponse):
    """题目详情模式"""
    test_cases: List[TestCaseResponse] = [] 