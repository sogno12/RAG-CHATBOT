from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

from app.services.chat_service import chat_with_context, chat_with_session, summarize_and_update_session, chat_with_summary
from app.utils.logger import logger

router = APIRouter()

@router.post("/chat")
async def chat(request: dict):
    query = request.get("query", "")
    history = request.get("history", [])
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query")

    result = await chat_with_context(query, history)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})


@router.post("/chat-session")
async def chat_session(request: dict, background_tasks: BackgroundTasks):
    user_id = request.get("user_id", "")
    session_id = request.get("session_id", [])
    query = request.get("query", "")

    # 챗 세션 응답
    result = await chat_with_session(user_id, session_id, query)

    # 응답 후 요약 작업 백그라운드에서 실행
    background_tasks.add_task(
        summarize_and_update_session, user_id, session_id, query, result["answer"]
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})

@router.post("/chat-summary")
async def chat_summary(request: dict, background_tasks: BackgroundTasks):
    user_id = request.get("user_id", "")
    session_id = request.get("session_id", [])
    query = request.get("query", "")

    # 챗 세션 응답
    result = await chat_with_summary(user_id, session_id, query)

    # 응답 후 요약 작업 백그라운드에서 실행
    background_tasks.add_task(
        summarize_and_update_session, user_id, session_id, query, result["answer"]
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})


