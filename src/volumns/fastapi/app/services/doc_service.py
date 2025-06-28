# src/volumns/fastapi/services/doc_service.py

import uuid
from datetime import datetime

from app.services.embed_service import split_text_into_chunks, get_embeddings
from app.chroma_db import get_chroma_client
from app.utils.logger import logger

def embed_and_store(content: str, filename: str = "unknown.txt") -> dict:
    # 1. 텍스트 → 청크 분할
    chunks = split_text_into_chunks(content)
    logger.info(f"📄 총 {len(chunks)}개의 청크로 분할됨")

    # 등록 시간 추가 (ISO 형식)
    uploaded_at = datetime.now().isoformat()

    # 2. 임베딩 생성
    embeddings = get_embeddings(chunks)

    # 3. UUID + 메타데이터 구성
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": filename, "uploaded_at": uploaded_at} for _ in chunks]

    # 4. ChromaDB 저장
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name="default")

    logger.info(f"📌 저장 전 컬렉션 총 문서 수: {collection.count()}")
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )
    logger.info(f"📌 저장 후 컬렉션 총 문서 수: {collection.count()}")

    return {
        "status": "success",
        "filename": filename,
        "chunks_stored": len(chunks),
        "ids": ids
    }


def get_uploaded_documents() -> list[dict]:
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name="default")
    all_data = collection.get()
    
    docs = []
    for uid, meta in zip(all_data.get("ids", []), all_data.get("metadatas", [])):
        if meta and "source" in meta:
            docs.append({
                "uuid": uid,
                "source": meta["source"],
                "uploaded_at": meta.get("uploaded_at", "N/A")
            })
    return docs

# documents uuid 기준으로 삭제
def delete_document_by_id(uuid: str):
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name="default")
    collection.delete(ids=[uuid])
