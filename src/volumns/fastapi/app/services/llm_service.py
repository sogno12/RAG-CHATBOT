# app/services/llm_service.py
from fastapi import status
import requests
import os
import time
from typing import Optional

from app.utils.logger import logger
from app.services.log_service import log_llm_response

VLLM_SERVER_URL = os.getenv("VLLM_SERVER_URL", "http://localhost:48000")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "/models/gemma2-9b-it")

def check_llm_connection() -> bool:
    try:
        res = requests.get(f"{VLLM_SERVER_URL}/v1/models", timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def get_llm_models() -> dict:
    """LLM 서버의 /v1/models 전체 응답 반환"""
    try:
        res = requests.get(f"{VLLM_SERVER_URL}/v1/models", timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"status": "error", "message": f"LLM 서버 응답 오류: {e}"}

def call_llm(
    query: str,
    context: str,
    parameter_setting: Optional[dict] = None
) -> tuple[str, dict]:
    # 기본 파라미터
    default_setting = {
        "model": DEFAULT_MODEL,
        "max_tokens": 512,
        "temperature": 0.7,
    }
    
    # 받은 설정으로 덮어쓰기
    setting = {**default_setting, **(parameter_setting or {})}

    # prompt 구성
    prompt = f"[문서 요약]\n{context}\n\n[사용자 질문]\n{query}"

    response = requests.post(
        f"{VLLM_SERVER_URL}/v1/completions",
        json={**setting, "prompt": prompt},
        timeout=30
    )
    response.raise_for_status()
    res_json = response.json()
    answer = res_json["choices"][0]["text"]
    usage = res_json.get("usage", {})
    return answer, usage


async def call_llm_with_logging(
    query: str,
    context: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    from uuid import uuid4
    from datetime import datetime, timedelta, timezone

    KST = timezone(timedelta(hours=9))

    start = time.time()
    request_id = str(uuid4())
    request_at = datetime.now(KST).isoformat()

    parameter_setting = {
        "temperature": 0.7,
        "max_tokens": 512
    }

    answer = ""
    usage = {}
    is_error = False
    error_type = None
    error_message = None
    status_code = status.HTTP_200_OK

    try:
        answer, usage = call_llm(query, context, parameter_setting)
    except Exception as e:
        is_error = True
        error_type = type(e).__name__
        error_message = str(e)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        answer = f"[ERROR] LLM 호출 실패: {error_message}"
    finally:
        # 소요시간
        elapsed = time.time() - start

        # 로깅
        await log_llm_response(
            request_id=request_id,
            request_at=request_at,
            query=query,
            response=answer,
            elapsed=elapsed,
            context=context,
            user_id=user_id,
            session_id=session_id,
            is_error=is_error,
            error_type=error_type,
            error_message=error_message,
            status_code=status_code,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            parameter_setting=parameter_setting,
        )

    return answer
