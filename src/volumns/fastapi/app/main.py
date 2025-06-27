from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.services.embed_service import embed_and_store
from app.services.search_service import search_similar_docs
from app.services.chat_service import chat_with_context, llm_health_check, get_llm_status_verbose
from app.services.session_service import chat_with_session

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

@app.get("/llm-status")
def llm_status():
    return llm_health_check()

@app.post("/chat")
async def chat(request: dict):
    query = request.get("query", "")
    history = request.get("history", [])
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query")

    result = chat_with_context(query, history)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})

@app.get("/llm-status/detail")
def llm_status_detail():
    return get_llm_status_verbose()

@app.post("/chat-session")
async def chat_session(request: dict):
    print("✅ chat_session 진입")
    user_id = request.get("user_id", "")
    session_id = request.get("session_id", [])
    query = request.get("query", "")
    result = chat_with_session(user_id, session_id, query)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "result": result})

