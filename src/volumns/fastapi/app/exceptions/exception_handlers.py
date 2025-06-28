# app/exceptions/exception_handlers.py

"""
# 참고 가능한 주요 상태 코드 상수
| 이름                                    | 값     |
| --------------------------------------- | ----- |
| `status.HTTP_200_OK`                    | `200` |
| `status.HTTP_201_CREATED`               | `201` |
| `status.HTTP_400_BAD_REQUEST`           | `400` |
| `status.HTTP_401_UNAUTHORIZED`          | `401` |
| `status.HTTP_403_FORBIDDEN`             | `403` |
| `status.HTTP_404_NOT_FOUND`             | `404` |
| `status.HTTP_422_UNPROCESSABLE_ENTITY`  | `422` |
| `status.HTTP_500_INTERNAL_SERVER_ERROR` | `500` |
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("FastAPI")

# 404, 403, 401 등 HTTP 예외
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"❗ HTTP Exception: {exc.status_code} {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "code": exc.status_code
        },
    )

# 422 Validation 에러
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("⚠️ Validation Error", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "fail",
            "message": "Invalid request parameters",
            "details": exc.errors()
        },
    )

# 500 등 일반 예외
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("🔥 Unhandled Exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error"
        },
    )
