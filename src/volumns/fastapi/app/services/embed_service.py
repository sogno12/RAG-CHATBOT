# embed.py
import uuid
from typing import List

from ..chroma_db import get_chroma_client
from ..model_loader import get_embedding_model

from app.utils.logger import logger

def get_embeddings(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True).tolist()

# ✅ 텍스트를 청크로 분할하는 함수
def split_text_into_chunks(text: str, max_chunk_size: int = 500) -> List[str]:
    lines = text.strip().splitlines()
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) <= max_chunk_size:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# ✅ 메인 처리 함수
def embed_and_store(content: str, filename: str = "unknown.txt") -> dict:
    # 1. 청크 분할
    chunks = split_text_into_chunks(content)

    # 2. 임베딩 생성
    embeddings = get_embeddings(chunks)

    # 3. UUID 생성 + 메타데이터
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": filename} for _ in chunks]

    # 4. Chroma 컬렉션에 저장
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name="default")
    
    logger.info("📌 Collection count (before):", collection.count())
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )

    logger.info("📌 Collection count (after):", collection.count())

    return {"status": "success", "chunks_stored": len(chunks), "ids": ids}

