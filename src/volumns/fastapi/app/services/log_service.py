# services/log_service.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from app.db.mongodb import db  # db 연결 객체

# 한국 시간(KST, UTC+9) 타임존 객체
KST = timezone(timedelta(hours=9))

async def log_llm_response(
    query: str,
    response: str,
    elapsed: float,
    context: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    log_doc = {
        "query": query,
        "response": response,
        "response_time": elapsed,
        "created_at": datetime.now(KST)
    }

    if context is not None:
        log_doc["context"] = context

    if user_id:
        log_doc["user_id"] = user_id
    if session_id:
        log_doc["session_id"] = session_id

    await db["llm_logs"].insert_one(log_doc)