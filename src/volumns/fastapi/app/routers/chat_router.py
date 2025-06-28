from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

from app.services.chat_service import chat_with_context, chat_with_session
from app.utils.logger import logger

router = APIRouter()

@router.post("/chat")
async def chat(request: dict):
    query = request.get("query", "")
    history = request.get("history", [])
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query")

    result = chat_with_context(query, history)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})


@router.post("/chat-session")
async def chat_session(request: dict):
    user_id = request.get("user_id", "")
    session_id = request.get("session_id", [])
    query = request.get("query", "")
    result = chat_with_session(user_id, session_id, query)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})

