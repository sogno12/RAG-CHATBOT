# search_doc.py
from .chroma_db import get_chroma_client
from .model_loader import get_embedding_model

def search_similar_docs(query: str, top_k: int = 3):
    chroma = get_chroma_client()
    collection = chroma.get_or_create_collection(name="default")

    model = get_embedding_model()
    query_embedding = model.encode([query], convert_to_numpy=True).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results
