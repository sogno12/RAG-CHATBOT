# embed.py
import uuid
from typing import List
from .chroma_db import get_chroma_client

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

# ✅ 예시 임베딩 생성 함수 (모델 없이 임시값)
def generate_fake_embeddings(chunks: List[str]) -> List[List[float]]:
    return [[0.0] * 768 for _ in chunks]

# ✅ 메인 처리 함수
def embed_and_store(content: str) -> dict:
    # 1. 청크 분할
    chunks = split_text_into_chunks(content)

    # 2. 임베딩 생성
    embeddings = generate_fake_embeddings(chunks)

    # 3. UUID 생성
    ids = [str(uuid.uuid4()) for _ in chunks]

    # 4. Chroma 컬렉션에 저장
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name="default")

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
    )

    return {"status": "success", "chunks_stored": len(chunks)}
