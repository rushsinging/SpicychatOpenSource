import redis
import json
import os
from typing import Optional

# Redis 客户端配置
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),  # Redis 服务器地址
    port=os.getenv("REDIS_PORT", 6379),        # Redis 端口
    db=os.getenv("REDIS_DB", 0),            # 使用的数据库编号
    decode_responses=True  # 自动解码响应
)

def get_session(session_id: str):
    data = redis_client.get(session_id)
    return json.loads(data) if data else {}

def save_session(session_id: str, session: dict):
    redis_client.set(session_id, json.dumps(session))
