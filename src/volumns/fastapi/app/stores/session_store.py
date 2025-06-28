# src/volumns/fastapi/store/session_store.py

import os
import redis
import json
from typing import Dict, List
from app.utils.logger import logger

# .env를 통해 주입된 환경변수 사용
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
    logger.info(f"💾 get_user_sessions 호출: user_id={user_id}, session_ids={session_ids}")
    return session_ids

def delete_session(user_id: str, session_id: str):
    key = _make_key(user_id, session_id)
    r.delete(key)
    logger.info(f"🗑️ 세션 삭제 완료: {key}")

def clear_all_sessions(user_id: str):
    pattern = f"{SESSION_PREFIX}:{user_id}:*"
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)
    logger.info(f"🗑️ 전체 세션 삭제 완료: user_id={user_id}")
