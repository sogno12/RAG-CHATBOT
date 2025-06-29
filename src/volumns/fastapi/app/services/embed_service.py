# src/volumns/fastapi/services/embed_service.py
from typing import List

from app.model_loader import get_embedding_model
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
