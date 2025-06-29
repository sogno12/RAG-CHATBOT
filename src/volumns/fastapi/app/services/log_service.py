# services/log_service.py

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional

from app.utils.logger import logger
from app.db.mongodb import db  # db 연결 객체

# 한국 시간(KST, UTC+9) 타임존 객체
KST = timezone(timedelta(hours=9))

async def log_llm_response(
    query: str,
    response: str,
    elapsed: float,
    status_code: int,
    context: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    is_error: Optional[bool] = False,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    request_id: Optional[str] = None,
    request_at: Optional[str] = None,
    parameter_setting: Optional[dict] = None,
):
    log_doc = {
        "request_id": request_id or str(uuid4()),
        "request_at": request_at or datetime.now(KST).isoformat(),
        "query": query,
        "response": response,
        "response_time": elapsed,
        "status_code": status_code,
        "is_error": is_error,
        "created_at": datetime.now(KST),
    }

    # 선택 필드 추가
    if context:
        log_doc["context"] = context
    if user_id:
        log_doc["user_id"] = user_id
    if session_id:
        log_doc["session_id"] = session_id
    if prompt_tokens is not None:
        log_doc["prompt_tokens"] = prompt_tokens
    if completion_tokens is not None:
        log_doc["completion_tokens"] = completion_tokens
    if total_tokens is not None:
        log_doc["total_tokens"] = total_tokens
    if parameter_setting is not None:
        log_doc["parameter_setting"] = parameter_setting
    if is_error:
        log_doc["error_type"] = error_type
        log_doc["error_message"] = error_message

    try:
        await db["llm_logs"].insert_one(log_doc)
    except Exception as log_error:
        logger.error(f"[MongoDB Log 실패] {log_error}")