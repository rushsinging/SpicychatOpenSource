import os

import psycopg2
from psycopg2.extras import DictCursor

# PostgreSQL 客户端配置
postgres_client = psycopg2.connect(
    dsn=os.getenv("DATABASE_URL", "postgres://nsfw:nsfw@localhost:5433/nsfw"),
    cursor_factory=DictCursor
)
postgres_client.autocommit = True

def get_db():
    """获取数据库连接"""
    return postgres_client

def get_cursor():
    """获取数据库游标"""
    return postgres_client.cursor()
