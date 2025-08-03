#!/bin/bash

# OJ Backend 启动脚本

echo "Starting OJ Backend..."

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please edit .env file with your configuration"
fi

# 创建必要的目录
mkdir -p uploads logs

# 设置权限
chmod +x start.sh

# 检查是否在Docker环境中
if [ -f /.dockerenv ]; then
    echo "Running in Docker container..."
    
    # 等待数据库启动
    echo "Waiting for database to be ready..."
    while ! nc -z postgres 5432; do
        sleep 1
    done
    
    # 运行数据库迁移
    echo "Running database migrations..."
    alembic upgrade head
    
    # 启动应用
    echo "Starting FastAPI application..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    echo "Running in local environment..."
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        echo "Python3 is not installed. Please install Python 3.8+"
        exit 1
    fi
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # 运行数据库迁移
    echo "Running database migrations..."
    alembic upgrade head
    
    # 启动应用
    echo "Starting FastAPI application..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi 