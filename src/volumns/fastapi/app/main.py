from fastapi import FastAPI, UploadFile, File
from app.embed import embed_and_store

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI 서버가 실행 중입니다."}

@app.post("/upload-doc")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    result = embed_and_store(content.decode("utf-8"))
    return {"status": "ok", "result": result}
