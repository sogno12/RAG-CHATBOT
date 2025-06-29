from app.stores import session_store
from app.utils.logger import logger

# 세션 대화 이력 조회
def get_history(user_id: str, session_id: str):
    return session_store.get_history(user_id, session_id)

# 세션 메시지 저장
def save_message(user_id: str, session_id: str, message: dict):
    session_store.save_message(user_id, session_id, message)

# 사용자 전체 세션 목록 조회
def get_user_sessions(user_id: str):
    return session_store.get_user_sessions(user_id)

# 특정 세션 삭제
def delete_session(user_id: str, session_id: str):
    session_store.delete_session(user_id, session_id)

# 사용자 전체 세션 삭제
def clear_all_sessions(user_id: str):
    session_store.clear_all_sessions(user_id)

# 세션 요약 저장 (비동기)
def update_session_summary(user_id: str, session_id: str, summary: str):
    try:
        session_store.set_summary(user_id, session_id, summary)
    except Exception as e:
        logger.warning(f"[세션 요약 저장 실패] {session_id} - {e}")

# 세션 요약 조회 (비동기)
def get_session_summary(user_id: str, session_id: str) -> str:
    try:
        return session_store.get_summary(user_id, session_id)
    except Exception as e:
        logger.warning(f"[세션 요약 조회 실패] {session_id} - {e}")
        return ""
