from fastapi import FastAPI, File, UploadFile, HTTPException, Request

from app.embed import embed_and_store
from app.search_doc import search_similar_docs

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI 서버가 실행 중입니다."}

@app.post("/upload-doc")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    result = embed_and_store(content.decode("utf-8"))
    return {"status": "ok", "result": result}

@app.post("/search-doc")
async def search_doc(request: dict):
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
    results = search_similar_docs(query)
    return {"status": "ok", "result": results}
