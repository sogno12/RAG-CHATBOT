from sentence_transformers import SentenceTransformer

_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("BAAI/bge-m3", device="cpu")
    return _embed_model
