# OJ Backend 快速启动指南

## 使用Docker Compose快速部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd oj_backend
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量文件
# 修改SECRET_KEY和其他必要配置
```

### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 4. 访问服务
- API文档: http://localhost/docs
- 健康检查: http://localhost/health
- 主应用: http://localhost

## 本地开发环境

### 1. 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置数据库
```bash
# 启动PostgreSQL和Redis（需要单独安装）
# 或者使用Docker
docker run -d --name postgres -e POSTGRES_PASSWORD=oj_password -e POSTGRES_USER=oj_user -e POSTGRES_DB=oj_db -p 5432:5432 postgres:15
docker run -d --name redis -p 6379:6379 redis:7
```

### 3. 配置环境变量
```bash
cp env.example .env
# 编辑.env文件，设置正确的数据库连接
```

### 4. 运行数据库迁移
```bash
alembic upgrade head
```

### 5. 启动应用
```bash
uvicorn app.main:app --reload
```

## 测试

### 运行测试
```bash
pytest tests/
```

### 运行特定测试
```bash
pytest tests/test_auth.py -v
```

## API使用示例

### 1. 用户注册
```bash
curl -X POST "http://localhost/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword",
    "nickname": "Test User"
  }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword"
  }'
```

### 3. 获取用户信息
```bash
curl -X GET "http://localhost/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 常见问题

### 1. 数据库连接失败
- 检查PostgreSQL服务是否运行
- 确认数据库连接字符串正确
- 检查防火墙设置

### 2. Redis连接失败
- 检查Redis服务是否运行
- 确认Redis端口是否正确
- 检查网络连接

### 3. 评测服务无法启动
- 确保Docker已安装并运行
- 检查Docker权限设置
- 确认Docker网络配置

### 4. 端口冲突
- 修改docker-compose.yml中的端口映射
- 检查端口是否被其他服务占用

## 开发指南

### 添加新功能
1. 在`app/models/`中定义数据模型
2. 在`app/schemas/`中定义API模式
3. 在`app/services/`中实现业务逻辑
4. 在`app/api/v1/`中定义API路由
5. 在`tests/`中编写测试

### 数据库迁移
```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 代码格式化
```bash
# 使用black格式化代码
black app/

# 使用isort排序导入
isort app/
```

## 生产部署

### 1. 安全配置
- 修改所有默认密码
- 配置HTTPS证书
- 设置防火墙规则
- 启用日志监控

### 2. 性能优化
- 配置数据库连接池
- 启用Redis缓存
- 设置负载均衡
- 配置CDN

### 3. 监控告警
- 配置健康检查
- 设置日志聚合
- 配置性能监控
- 设置告警规则

## 技术支持

如果遇到问题，请：
1. 查看日志文件
2. 检查服务状态
3. 参考API文档
4. 提交Issue到项目仓库 