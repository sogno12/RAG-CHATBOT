# app/services/llm_service.py
import requests
import os

VLLM_SERVER_URL = os.getenv("VLLM_SERVER_URL", "http://localhost:48000")

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

def call_llm(prompt: str) -> str:
    return f"🤖 (모의 응답) '{prompt}' 에 대한 답변입니다."
