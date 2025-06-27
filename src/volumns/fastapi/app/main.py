from fastapi import FastAPI
from app.routers import chat_router, doc_router, search_router, llm_router
from app.utils.logger import logger

app = FastAPI()

logger.info("✅ FastAPI 앱 시작됨")

app.include_router(chat_router.router)
app.include_router(doc_router.router)
app.include_router(search_router.router)
app.include_router(llm_router.router)

@app.get("/")
def root():
    return {"message": "FastAPI 서버가 실행 중입니다."}
