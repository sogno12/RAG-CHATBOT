# app/services/chat_service.py
from fastapi import HTTPException
from typing import Union

from app.services.search_service import search_similar_docs
from app.services.llm_service import call_llm, call_llm_with_logging, check_llm_connection, get_llm_models
from app.services.session_service import get_history, save_message, update_session_summary, get_session_summary
from app.utils.logger import logger

def llm_health_check() -> dict:
    if check_llm_connection():
        return {"status": "ok", "message": "LLM 서버 연결 성공"}
    else:
        raise HTTPException(status_code=503, detail="LLM 서버에 연결할 수 없습니다.")

def get_llm_status_verbose() -> dict:
    return get_llm_models()


def build_prompt(query: str, docs: list[str], history: Union[str, list[dict]]) -> str:
    # 1. history_text 생성 방식 분기
    if isinstance(history, str):
        history_text = history
    elif isinstance(history, list):
        history_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
    else:
        history_text = "[이력 없음]"

    # 2. 문서 텍스트 정리
    docs_text = "\n".join(docs)

    return f"""
[Document Context]
{docs_text}

[Conversation History]
{history_text}

[User Question]
{query}
""".strip()


async def chat_with_context(query: str, history: list[dict]) -> dict:
    # 1. 벡터 검색
    retrieved_docs = search_similar_docs(query)

    # 2. 이전 대화기록 + 검색 결과로 LLM 호출
    prompt = build_prompt(query, retrieved_docs, history)
    answer = await call_llm_with_logging(query, prompt)

    return {
        "answer": answer,
        "context_docs": retrieved_docs
    }


async def chat_with_session(user_id: str, session_id: str, query: str) -> dict:

    # 1. 세션 이력 조회
    history = get_history(user_id, session_id)

    # 2. 벡터 검색
    retrieved_docs = search_similar_docs(query)
    logger.info(f"🔍 관련 문서 검색 완료 (총 {len(retrieved_docs)}개 문서)")

    # 3. 프롬프트 생성
    prompt = build_prompt(query, retrieved_docs, history)
    logger.info(f"🧱 프롬프트 생성 완료 (길이: {len(prompt)}자)\n프롬프트 일부:\n{prompt[:30]}...")

    # 4. LLM 호출
    answer = await call_llm_with_logging(query, prompt)

    # 5. 세션 저장
    save_message(user_id, session_id, {"role": "user", "content": query})
    save_message(user_id, session_id, {"role": "assistant", "content": answer})

    return {
        "query": query,
        "context_docs": retrieved_docs,
        "answer": answer
    }

async def chat_with_summary(user_id: str, session_id: str, query: str) -> dict:

    # 1. 세션 요약 정보 검색
    summary = get_session_summary(user_id, session_id)
    logger.info(f"🧠 세션 요약 정보 조회 완료: {summary[:30]}...")

    # 2. 벡터 검색
    retrieved_docs = search_similar_docs(query)
    logger.info(f"🔍 관련 문서 검색 완료 (총 {len(retrieved_docs)}개 문서)")

    # 3. 프롬프트 생성 (요약 기반 context 사용)
    prompt = build_prompt(query, retrieved_docs, summary)
    logger.info(f"🧱 프롬프트 생성 완료 (길이: {len(prompt)}자)\n프롬프트 일부:\n{prompt[:30]}...")

    # 4. LLM 호출
    answer = await call_llm_with_logging(query, prompt, user_id=user_id, session_id=session_id)

    # 5. 세션 저장
    save_message(user_id, session_id, {"role": "user", "content": query})
    save_message(user_id, session_id, {"role": "assistant", "content": answer})

    # 6. 결과 리턴
    return {
        "query": query,
        "context_docs": retrieved_docs,
        "answer": answer
    }


def summarize_and_update_session(user_id: str, session_id: str, query: str, answer: str):
    try:
        history = get_history(user_id, session_id)
        summary = summarize_messages(
            history + [{"role": "user", "content": query}, {"role": "assistant", "content": answer}]
        )
        update_session_summary(user_id, session_id, summary)
        logger.info(f"[요약 성공] {session_id} - {summary}")
    except Exception as e:
        logger.warning(f"[요약 실패] {session_id} - {e}")


# 요약 함수
def summarize_messages(history: list[dict]) -> str:
    conversation = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    prompt = f"[대화 요약]\n다음 대화를 간단히 요약해줘:\n{conversation}"
    answer, _ = call_llm("", prompt)  # ✅ answer만 사용
    return answer

