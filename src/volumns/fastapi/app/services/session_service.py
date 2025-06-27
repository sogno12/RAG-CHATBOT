# session_service.py
from app.stores import session_store
from app.services.llm_service import call_llm
from app.utils.logger import logger

def chat_with_session(user_id: str, session_id: str, query: str) -> dict:
    logger.info(f"✅ session_service 진입: user_id={user_id}, session_id={session_id}, query={query}")

    # 1. 과거 대화 이력 조회
    history = session_store.get_history(user_id, session_id)

    # 2. 유저 질문 저장
    session_store.save_message(user_id, session_id, {
        "role": "user",
        "content": query
    })

    # 3. history → 문자열 context 구성
    context = ""
    for turn in history:
        role = turn["role"]
        content = turn["content"]
        if role == "user":
            context += f"[사용자] {content}\n"
        elif role == "assistant":
            context += f"[응답] {content}\n"

    # 4. LLM 호출
    answer = call_llm(query=query, context=context)

    # 5. assistant 응답 저장
    session_store.save_message(user_id, session_id, {
        "role": "assistant",
        "content": answer
    })

    return {"context":context, "answer": answer}