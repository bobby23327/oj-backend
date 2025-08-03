"""
数据库连接和会话管理
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

from .config import settings


# 创建数据库引擎
def create_db_engine():
    """创建数据库引擎"""
    if settings.debug and "test" in settings.database_url.lower():
        # 测试环境使用内存数据库
        return create_engine(
            "sqlite:///./test.db",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        return create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
        )


# 创建异步数据库引擎
def create_async_db_engine() -> AsyncEngine:
    """创建异步数据库引擎"""
    if settings.debug and "test" in settings.database_url.lower():
        # 测试环境使用内存数据库
        return create_async_engine(
            "sqlite+aiosqlite:///./test.db",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # 将postgresql://转换为postgresql+asyncpg://
        async_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return create_async_engine(
            async_url,
            echo=settings.debug,
            pool_pre_ping=True,
        )


# 创建数据库引擎实例
engine = create_db_engine()
async_engine = create_async_db_engine()


def create_db_and_tables():
    """创建数据库和表"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


async def get_async_session() -> AsyncSession:
    """获取异步数据库会话"""
    async with AsyncSession(async_engine) as session:
        yield session


def init_db():
    """初始化数据库"""
    create_db_and_tables() 