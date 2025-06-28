# chroma_db.py
import chromadb

def get_chroma_client():
    # PersistentClient를 사용하여 클라이언트를 생성합니다.
    # 이 방식이 최신 버전에서 권장하는 방법입니다.
    return chromadb.PersistentClient(path="/chroma_db")