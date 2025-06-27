from sentence_transformers import SentenceTransformer

# 로컬에 마운트된 경로
MODEL_PATH = "/model/BGE-m3-ko"

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_PATH)
    return _model
