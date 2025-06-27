# app/services/chat_service.py

from app.services.search_service import search_similar_docs
from app.services.llm_service import call_llm  # (LLM 연동 함수가 이쪽에 있다고 가정)

def chat_with_context(query: str, history: list[dict]) -> dict:
    # 1. 벡터 검색
    retrieved_docs = search_similar_docs(query)

    # 2. 이전 대화기록 + 검색 결과로 LLM 호출
    prompt = build_prompt(query, retrieved_docs, history)
    answer = call_llm(prompt)

    return {
        "answer": answer,
        "context_docs": retrieved_docs
    }

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
