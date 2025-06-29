# app/services/llm_service.py
import requests
import os
import time

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

def call_llm(query: str, context: str) -> str:
    try:
        # prompt 구성
        prompt = f"[문서 요약]\n{context}\n\n[사용자 질문]\n{query}"

        response = requests.post(
            f"{VLLM_SERVER_URL}/v1/completions",
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7,
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"]
    except Exception as e:
        return f"[ERROR] LLM 호출 실패: {e}"
    
def call_llm_with_timing(query: str, prompt: str) -> tuple[str, float]:
    start = time.time()
    answer = call_llm(query, prompt)
    elapsed = time.time() - start
    return answer, elapsed