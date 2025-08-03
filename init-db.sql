-- 创建数据库和用户
CREATE DATABASE IF NOT EXISTS oj_db;
CREATE DATABASE IF NOT EXISTS oj_test_db;

-- 创建用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'oj_user') THEN
        CREATE USER oj_user WITH PASSWORD 'oj_password';
    END IF;
END
$$;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE oj_db TO oj_user;
GRANT ALL PRIVILEGES ON DATABASE oj_test_db TO oj_user;

-- 连接到主数据库
\c oj_db;

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建表（这些将由SQLModel自动创建，但这里提供一些基础结构）
-- 注意：实际的表结构将由Alembic迁移管理

-- 创建索引（可选）
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_problems_title ON problems(title);
-- CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id);
-- CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id);
-- CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status); 