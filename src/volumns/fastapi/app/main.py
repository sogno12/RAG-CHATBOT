from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.services.embed_service import embed_and_store
from app.services.search_service import search_similar_docs

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI 서버가 실행 중입니다."}

@app.post("/upload-doc")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    result = embed_and_store(content.decode("utf-8"), filename=filename)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})

@app.post("/search-doc")
async def search_doc(request: dict):
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query")
    results = search_similar_docs(query)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": results})
