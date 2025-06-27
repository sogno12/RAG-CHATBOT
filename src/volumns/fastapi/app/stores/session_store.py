# src/volumns/fastapi/store/session_store.py

from typing import Dict, List

_session_db: Dict[str, Dict[str, List[Dict]]] = {}

def get_history(user_id: str, session_id: str) -> List[Dict]:
    print(f"📂 get_history 호출: user_id={user_id}, session_id={session_id}")
    return _session_db.get(user_id, {}).get(session_id, [])

def save_message(user_id: str, session_id: str, message: Dict):
    print(f"💾 save_message 호출: user_id={user_id}, session_id={session_id}, message={message}")
    if user_id not in _session_db:
        _session_db[user_id] = {}
    if session_id not in _session_db[user_id]:
        _session_db[user_id][session_id] = []
    _session_db[user_id][session_id].append(message)

def get_user_sessions(user_id: str) -> List[str]:
    return list(_session_db.get(user_id, {}).keys())
