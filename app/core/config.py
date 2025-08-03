"""
应用配置管理
"""
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本设置
    app_name: str = Field(default="OJ Backend", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    
    # 安全设置
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 数据库设置
    database_url: str = Field(..., env="DATABASE_URL")
    database_test_url: Optional[str] = Field(default=None, env="DATABASE_TEST_URL")
    
    # Redis设置
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # Celery设置
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND")
    
    # 评测设置
    judge_timeout: int = Field(default=10, env="JUDGE_TIMEOUT")
    judge_memory_limit: int = Field(default=512, env="JUDGE_MEMORY_LIMIT")
    judge_cpu_limit: float = Field(default=1.0, env="JUDGE_CPU_LIMIT")
    
    # Docker评测设置
    judge_docker_image: str = Field(default="oj-judge:latest", env="JUDGE_DOCKER_IMAGE")
    judge_docker_network: str = Field(default="oj-network", env="JUDGE_DOCKER_NETWORK")
    
    # 文件存储设置
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    # CORS设置
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # 日志设置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/oj_backend.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings() 