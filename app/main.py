"""
FastAPI主应用入口
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, users, problems, submissions, judge, ranks, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("Starting OJ Backend...")
    init_db()
    print("Database initialized")
    
    yield
    
    # 关闭时执行
    print("Shutting down OJ Backend...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于FastAPI的在线评测系统后端",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 在生产环境中应该限制允许的主机
)

# 包含API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(problems.router, prefix="/api/v1/problems", tags=["题目"])
app.include_router(submissions.router, prefix="/api/v1/submissions", tags=["提交"])
app.include_router(judge.router, prefix="/api/v1/judge", tags=["评测"])
app.include_router(ranks.router, prefix="/api/v1/ranks", tags=["排行榜"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to OJ Backend",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 