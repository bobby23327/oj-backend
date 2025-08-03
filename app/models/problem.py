"""
题目和测试用例数据模型
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class ProblemDifficulty(str, Enum):
    """题目难度枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemStatus(str, Enum):
    """题目状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Problem(SQLModel, table=True):
    """题目模型"""
    __tablename__ = "problems"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: str = Field(max_length=10000)  # Markdown格式
    difficulty: ProblemDifficulty = Field(default=ProblemDifficulty.EASY)
    status: ProblemStatus = Field(default=ProblemStatus.DRAFT)
    
    # 限制条件
    time_limit: int = Field(default=1000)  # 毫秒
    memory_limit: int = Field(default=256)  # MB
    output_limit: int = Field(default=1024)  # KB
    
    # 统计信息
    total_submissions: int = Field(default=0)
    accepted_submissions: int = Field(default=0)
    acceptance_rate: float = Field(default=0.0)
    
    # 创建者信息
    created_by: int = Field(foreign_key="users.id")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)
    
    # 关系
    test_cases: List["TestCase"] = Relationship(back_populates="problem")
    submissions: List["Submission"] = Relationship(back_populates="problem")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "两数之和",
                "description": "给定一个整数数组 nums 和一个整数目标值 target...",
                "difficulty": "easy",
                "time_limit": 1000,
                "memory_limit": 256
            }
        }


class TestCase(SQLModel, table=True):
    """测试用例模型"""
    __tablename__ = "test_cases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    problem_id: int = Field(foreign_key="problems.id")
    name: str = Field(max_length=100)
    input_data: str = Field(max_length=10000)
    expected_output: str = Field(max_length=10000)
    is_sample: bool = Field(default=False)  # 是否为样例
    is_hidden: bool = Field(default=False)  # 是否为隐藏测试用例
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    problem: Problem = Relationship(back_populates="test_cases")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "样例1",
                "input_data": "2 7 11 15\n9",
                "expected_output": "0 1",
                "is_sample": True,
                "is_hidden": False
            }
        } 