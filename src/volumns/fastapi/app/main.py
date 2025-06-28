from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import chat_router, doc_router, search_router, llm_router, session_router
from app.utils.logger import logger
from app.exceptions import exception_handlers

app = FastAPI()

logger.info("✅ FastAPI 앱 시작됨")

# 예외 핸들러 등록
app.add_exception_handler(Exception, exception_handlers.general_exception_handler)
app.add_exception_handler(StarletteHTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)

# API 라우터 등록
app.include_router(chat_router.router)
app.include_router(doc_router.router)
app.include_router(search_router.router)
app.include_router(llm_router.router)
app.include_router(session_router.router)

@app.get("/")
def root():
    return {"message": "FastAPI 서버가 실행 중입니다."}
