"""
认证相关的测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash


# 创建测试数据库
@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # 创建表
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


# 创建测试客户端
@pytest.fixture
def client(test_db):
    def override_get_session():
        yield test_db
    
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_register_user(client, test_db):
    """测试用户注册"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "nickname": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["nickname"] == user_data["nickname"]
    assert "id" in data


def test_login_user(client, test_db):
    """测试用户登录"""
    # 先创建用户
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "nickname": "Test User"
    }
    
    client.post("/api/v1/auth/register", json=user_data)
    
    # 测试登录
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_db):
    """测试无效凭据登录"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_register_duplicate_username(client, test_db):
    """测试重复用户名注册"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "nickname": "Test User"
    }
    
    # 第一次注册
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    # 第二次注册相同用户名
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"] 