"""
提交数据模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class SubmissionStatus(str, Enum):
    """提交状态枚举"""
    PENDING = "pending"      # 排队中
    JUDGING = "judging"      # 评测中
    ACCEPTED = "accepted"    # 通过
    WRONG_ANSWER = "wrong_answer"  # 答案错误
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"  # 超时
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"  # 内存超限
    RUNTIME_ERROR = "runtime_error"  # 运行时错误
    COMPILATION_ERROR = "compilation_error"  # 编译错误
    SYSTEM_ERROR = "system_error"  # 系统错误


class ProgrammingLanguage(str, Enum):
    """编程语言枚举"""
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


class Submission(SQLModel, table=True):
    """提交模型"""
    __tablename__ = "submissions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    problem_id: int = Field(foreign_key="problems.id")
    
    # 提交信息
    code: str = Field(max_length=50000)  # 代码内容
    language: ProgrammingLanguage = Field(default=ProgrammingLanguage.PYTHON)
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING)
    
    # 评测结果
    score: Optional[int] = Field(default=None)  # 得分
    execution_time: Optional[int] = Field(default=None)  # 执行时间(ms)
    memory_used: Optional[int] = Field(default=None)  # 内存使用(MB)
    
    # 错误信息
    error_message: Optional[str] = Field(default=None, max_length=2000)
    compile_error: Optional[str] = Field(default=None, max_length=2000)
    
    # 测试用例结果
    passed_tests: Optional[int] = Field(default=None)
    total_tests: Optional[int] = Field(default=None)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    judged_at: Optional[datetime] = Field(default=None)
    
    # 关系
    user: "User" = Relationship(back_populates="submissions")
    problem: "Problem" = Relationship(back_populates="submissions")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def two_sum(nums, target):\n    # 实现代码\n    pass",
                "language": "python",
                "status": "pending"
            }
        } 