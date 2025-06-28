from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.session_service import get_user_sessions, get_history, clear_all_sessions, delete_session
from app.utils.logger import logger

router = APIRouter(prefix="/sessions", tags=["Session"])

# 1. 세션 목록 조회
@router.get("")
async def list_sessions(user_id: str = Query(...)):
    logger.info(f"📥 세션 목록 조회: user_id={user_id}")
    sessions = get_user_sessions(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "sessions": sessions}
    )

# 2. 단일 세션 조회
@router.get("/{session_id}")
async def get_session(session_id: str, user_id: str = Query(...)):
    logger.info(f"📥 단일 세션 조회: user_id={user_id}, session_id={session_id}")
    history = get_history(user_id, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "session_id": session_id, "history": history}
    )

# 3. 단일 세션 삭제
@router.delete("/{session_id}")
async def delete_session_by_session_id(session_id: str, user_id: str = Query(...)):
    logger.info(f"🗑️ 단일 세션 삭제: user_id={user_id}, session_id={session_id}")
    delete_session(user_id, session_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "message": "session deleted"}
    )

# 4. 전체 세션 삭제
@router.delete("/")
async def clear_sessions(user_id: str = Query(...)):
    logger.info(f"🗑️ 전체 세션 삭제 요청: user_id={user_id}")
    clear_all_sessions(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok", "message": "all sessions deleted"}
    )
