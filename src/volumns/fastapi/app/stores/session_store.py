# src/volumns/fastapi/store/session_store.py

import os
import redis
import json
from typing import Dict, List
from app.utils.logger import logger

# .env를 통해 주입된 환경변수 사용 (python-dotenv 불필요)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_SESSION_TTL = int(os.getenv("REDIS_SESSION_TTL", "3600"))

# Redis 클라이언트 초기화
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True  # 문자열 자동 디코딩
)

SESSION_PREFIX = "session"

def _make_key(user_id: str, session_id: str) -> str:
    return f"{SESSION_PREFIX}:{user_id}:{session_id}"

def get_history(user_id: str, session_id: str) -> List[Dict]:
    logger.info(f"📂 get_history 호출: user_id={user_id}, session_id={session_id}")
    key = _make_key(user_id, session_id)
    data = r.get(key)
    return json.loads(data) if data else []

def save_message(user_id: str, session_id: str, message: Dict):
    logger.info(f"💾 save_message 호출: user_id={user_id}, session_id={session_id}, message={message}")
    key = _make_key(user_id, session_id)
    history = get_history(user_id, session_id)
    history.append(message)
    r.set(key, json.dumps(history), ex=REDIS_SESSION_TTL)

def get_user_sessions(user_id: str) -> List[str]:
    pattern = f"{SESSION_PREFIX}:{user_id}:*"
    keys = r.keys(pattern)
    session_ids = [key.split(":")[2] for key in keys]
    return session_ids
