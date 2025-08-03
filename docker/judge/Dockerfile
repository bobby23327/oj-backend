# 使用Python 3.11官方镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        docker.io \
        curl \
        gcc \
        g++ \
        openjdk-11-jdk \
        nodejs \
        npm \
        golang-go \
        rustc \
        cargo \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制评测代码
COPY judge.py .

# 创建评测目录
RUN mkdir -p /app/judge_workspace /app/uploads

# 设置权限
RUN chmod +x /app/judge.py

# 启动命令
CMD ["python", "judge.py"] 