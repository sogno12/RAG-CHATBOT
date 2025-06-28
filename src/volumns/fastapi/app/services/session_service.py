# session_service.py
from app.stores import session_store

def get_history(user_id: str, session_id: str):
    return session_store.get_history(user_id, session_id)

def save_message(user_id: str, session_id: str, message: dict):
    session_store.save_message(user_id, session_id, message)

def get_user_sessions(user_id: str):
    return session_store.get_user_sessions(user_id)

def delete_session(user_id: str, session_id: str):
    session_store.delete_session(user_id, session_id)

def clear_all_sessions(user_id: str):
    session_store.clear_all_sessions(user_id)
