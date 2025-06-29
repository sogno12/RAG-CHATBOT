# app/services/chat_service.py
from fastapi import HTTPException

from app.services.search_service import search_similar_docs
from app.services.llm_service import call_llm_with_timing, check_llm_connection, get_llm_models
from app.services.session_service import get_history, save_message
from app.services.log_service import log_llm_response
from app.utils.logger import logger

def llm_health_check() -> dict:
    if check_llm_connection():
        return {"status": "ok", "message": "LLM 서버 연결 성공"}
    else:
        raise HTTPException(status_code=503, detail="LLM 서버에 연결할 수 없습니다.")

def get_llm_status_verbose() -> dict:
    return get_llm_models()


def build_prompt(query: str, docs: list[str], history: list[dict]) -> str:
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
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
    answer, elapsed = call_llm_with_timing(query, prompt)

    # ✅ log 저장
    await log_llm_response(
        query=query,
        response=answer,
        elapsed=elapsed,
        context=prompt
    )

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
    answer, elapsed = call_llm_with_timing(query, prompt)

    # 5. 세션 저장
    save_message(user_id, session_id, {"role": "user", "content": query})
    save_message(user_id, session_id, {"role": "assistant", "content": answer})

    # ✅ log 저장
    await log_llm_response(
        query=query,
        response=answer,
        elapsed=elapsed,
        context=prompt,
        user_id=user_id,        # 추가
        session_id=session_id   # 추가
    )

    return {
        "query": query,
        "context_docs": retrieved_docs,
        "answer": answer
    }
