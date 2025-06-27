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

def call_llm(prompt: str) -> str:
    return f"🤖 (모의 응답) '{prompt}' 에 대한 답변입니다."
