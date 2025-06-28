# utils/logger.py
import logging
import os
from datetime import datetime

# logs 디렉토리 존재 확인 및 없으면 생성
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 오늘 날짜 기반 로그 파일 이름
today_str = datetime.now().strftime("%Y-%m-%d")
fastapi_log_file = os.path.join(log_dir, f"FastAPI_{today_str}.log")
access_log_file = os.path.join(log_dir, f"access_{today_str}.log")

# 로그 포맷
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

# 파일 핸들러
file_handler = logging.FileHandler(fastapi_log_file, encoding="utf-8")
file_handler.setFormatter(formatter)

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 애플리케이션 로거: FastAPI.log 파일
app_logger = logging.getLogger("FastAPI")
app_logger.setLevel(logging.INFO)
app_logger.addHandler(file_handler)
app_logger.addHandler(console_handler)

# === uvicorn.error 로거 설정 ===
# 설명: FastAPI 실행 중 발생하는 에러, 경고, 정보 로그 등을 다룹니다.
# - 예: 서버 시작 로그, 예외 처리 로그 등
# - FastAPI 내부 코드에서 발생하는 예외도 이쪽으로 출력됩니다.
uvicorn_logger = logging.getLogger("uvicorn.error")
uvicorn_logger.setLevel(logging.INFO)  # 로그 레벨 설정
uvicorn_logger.addHandler(file_handler)     # 로그 파일 저장 (FastAPI_YYYY-MM-DD.log)
uvicorn_logger.addHandler(console_handler)  # 콘솔 출력

# === uvicorn.access 로거 설정 ===
# 설명: HTTP 요청 접근 로그를 다룹니다.
# - 예: 클라이언트 요청 (GET, POST), 응답 코드 (200, 404 등), 요청 시간, IP 주소 등
# - 웹 서버 접근 로그(access.log)와 동일한 역할
access_handler = logging.FileHandler(access_log_file, encoding="utf-8")
access_handler.setFormatter(formatter)

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.INFO)     # 로그 레벨 설정
uvicorn_access_logger.addHandler(access_handler) # access 로그 파일 저장 (access_YYYY-MM-DD.log)
uvicorn_access_logger.addHandler(console_handler) # 콘솔에도 동시에 출력


# logger.py 마지막에 이 줄 추가:
logger = app_logger