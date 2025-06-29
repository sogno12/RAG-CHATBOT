# 목표: RAG 사용하는 챗봇 만들기


v0.2. 기본 기능 구현

| 단계 | 작업 내용                           | 도구/기술                        | 설명                                           |
| -- | ----------------------------------- | ------------------------------- | -------------------------------------------- |
| A  | 예외 핸들러                    |                                                                         | 예외 핸들러 별도 파일로 관리                                                                                                       |
| 6  | 세션 선택/삭제/초기화 기능           | **FastAPI, Redis**                                                      | 사용자 세션을 리스트업하거나 초기화/삭제할 수 있는 API 추가                                                                                    |
| 7  | 업로드 문서 관리 기능              | **FastAPI, ChromaDB**                                                   | 업로드한 문서 조회 및 제거하는 기능                                                                                                   |
| B  | 세션 및 챗 서비스 구조 리팩터링        |                                                                         | 세션 및 서비스 파일 구조 재정비                                                                                                     |
| 8  | 문서 업로드 & 임베딩 구조 정리        | **FastAPI, ChromaDB, sentence-transformers, PyMuPDF, python-docx, bs4** | 다양한 입력 소스(txt, pdf, docx, URL)를 수용할 수 있도록 파서 구조를 `doc_service` 중심으로 통합하고, 벡터 임베딩 및 저장 과정을 분리하여 확장성 있는 문서 처리 파이프라인을 완성함 |
| 9  | MongoDB 로그 서버 구현          | **MongoDB, Motor, FastAPI**                                             | LLM 응답 시간, context 길이, query, response 등을 MongoDB에 저장하는 로그 수집 기능 구현. `llm_logs` 컬렉션에 저장하며 통계/시각화 기반 마련                 |
| 10 | LLM 응답 시간 및 context 길이 로깅 | **time, FastAPI logger**                                                | 로그 저장 외에도 콘솔 또는 파일로 context 길이 및 LLM 응답 시간 기록                                                                          |
| 11 | 대화 요약 기능 추가 | **FastAPI, Redis, vLLM** | 세션 대화 히스토리를 요약하여 Redis에 저장하고, 이후 질문 시 요약된 내용을 활용하여 context 길이를 줄이는 기능 추가. `background_tasks`를 활용해 응답 후 요약 비동기 처리함. |
| 12 | 검색 결과 chunk 하이라이트 또는 로깅   | **ChromaDB, FastAPI**                                                   | RAG가 어떤 chunk를 검색에 사용했는지 시각화하거나 로그에 남김                                                                                 |
| 13 | 간단한 인증 또는 사용자별 문서 분리      | **API Key, JWT, 사용자 ID 처리**                                             | 사용자 인증을 통해 데이터 분리 및 보안 강화                                                                                              |



-----


## A. 예외 핸들러

1. 예외 핸들러 별도 파일로 관리 : `app/exceptions/exception_handlers.py`
  -  FastAPI 프로젝트에서 모든 에러 응답을 일관된 JSON 포맷으로 처리

2. `main.py` 에서 등록

```python
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions import exception_handlers  # 추가

app = FastAPI()

# 예외 핸들러 등록
app.add_exception_handler(Exception, exception_handlers.general_exception_handler)
app.add_exception_handler(StarletteHTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)
```


3. 테스트
```bash
# 존재하지 않는 경로 → 404
curl http://localhost:48001/invalid-path

# 필수 파라미터 빠짐 → 422
curl http://localhost:48001/sessions

# 일부러 서버 오류 유도
# (예: 세션 조회에 user_id 빼먹고 내부 코드에서 None 접근하도록 수정해 테스트)
```


---

## 6. 세션 조회/삭제/초기화 기능

### 1) API 명세

| 설명              | 메서드      | URL                   |
| ---------------- | --------- | --------------------- |
| 세션 목록 조회     | `GET`    | `/sessions?user_id=user123`  |
| 단일 세션 상세 조회 | `GET`    | `/sessions/{session_id}?user_id=user123` |
| 세션 삭제         | `DELETE`  | `/session/{session_id}`  |
| 전체 세션 삭제     | `DELETE` | `/sessions?user_id=user123` |


### 2) 소스코드 작성

1. `session_store.py` 확장 코드
  - delete_session() 추가
  - clear_all_sessions() 추가

2. 라우터
  - `session_router.py` : FastAPI 라우터 구현
  - `main.py` : session_router 등록

### 3) 테스트

```bash
# 1. 세션 목록 조회
curl "http://localhost:48001/sessions?user_id=user123"

# 2. 단일 세션 조회
curl "http://localhost:48001/sessions/sess001?user_id=user123"

# 3. 단일 세션 삭제
curl -X DELETE "http://localhost:48001/sessions/sess001?user_id=user123"

# 4. 전체 세션 삭제
curl -X DELETE "http://localhost:48001/sessions?user_id=user123"
```

---

## 7. 업로드 문서 관리 기능

### 1) API 설계

| 설명            | 메서드      | URL                   |
| ------------- | -------- | --------------------- |
| 업로드한 문서 목록 조회 | `GET`    | `/documents`          |
| 특정 문서 삭제      | `DELETE` | `/documents/{source}` |

### 2) 소스코드 작성 

1. 서비스 분리
  - `embed_service.py` : 순수 기능 유틸성 함수 (임베딩 및 청크 분할)
  - `doc_service.py` : 문서 저장/관리/삭제 처리자

2. 라우터
  - `doc_router.py` : FastAPI 라우터 구현

### 3) 테스트

```bash
# 파일 업로드
curl -X POST http://localhost:48001/documents/upload-doc \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/test_doc.txt"

# 업로드된 문서 목록 조회
curl -X GET http://localhost:48001/documents

# 문서 삭제 요청
# 정상 요청 (성공) : uuid 맞게 변경
curl -X DELETE "http://localhost:48001/documents/test.txt" \
  -H "Content-Type: application/json" \
  -d '{"uuid": "279910e8-07e8-4b6c-8b53-d7a120da5b5e"}'
# 오류 요청 (uuid 누락)
curl -X DELETE "http://localhost:48001/documents/test.txt" \
  -H "Content-Type: application/json" \
  -d '{}'

```

---

## B. 세션 및 챗 서비스 구조 리팩터링

### 1) 세션 기능을 session_service 중심으로 분리

> 문제: 기존에는 session_router.py가 session_store.py를 직접 호출하여 Redis와 바로 통신
> → 이는 로직 분리 원칙에 어긋나며, 향후 세션 저장소 교체(예: DB) 시 유연성이 떨어짐

1. `session_service.py` 생성 및 다음 기능을 위임:
  - 세션 목록 조회 (get_user_sessions)
  - 단일 세션 조회 (get_history)
  - 단일 세션 삭제 (delete_session)
  - 전체 세션 삭제 (clear_all_sessions)

2. `session_router.py` 수정
  -  session_store를 직접 import 하지 않고 무조건 session_service를 통해 접근하도록 변경

### 2) 챗 기능을 chat_service 중심으로 정리

> 문제: chat_with_session() 위치가 chat 서비스의 역할을 하면서도 session 중심 구조로 흩어져 있어 RAG 파이프라인 구조와 맞지 않음

1. `chat_with_session()` 메소드를 → `chat_service.py`로 이동
2. `chat_with_session()` 도 RAG 파이프라인을 따르게 변경
  - chat_with_context() 구조처럼 `search_similar_docs()` → `build_prompt()` → `call_llm()` 흐름을 동일하게 적용


### 3) 테스트

```bash
# 세션 기반 챗 테스트 명령어
curl -X POST http://localhost:48001/chat-session \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session001",
    "query": "한국의 수도는 어디인가요?"
}'
```

---


## 8. 문서 업로드 & 임베딩 구조 정리

> 다양한 형식의 문서(txt, pdf, docx, url)를 지원하여 RAG 기반 질의에 활용될 수 있도록 텍스트를 추출하고, 벡터로 임베딩하여 DB에 저장하는 흐름 구축

1. 책임 분리 구조

| 모듈      | 파일명                 | 역할 및 책임                                                            |
| ------- | ------------------- | ------------------------------------------------------------------ |
| **라우터** | `doc_router.py`     | - 업로드 API 정의<br>- 업로드된 파일 또는 URL을 받아 서비스에 전달                       |
| **서비스** | `doc_service.py`    | - 입력 받은 파일/URL에서 텍스트 추출 **(파서 호출)**<br>- 청크 분리 → 임베딩 → ChromaDB 저장 |
| **유틸**  | `parse_document.py` | - `txt`, `pdf`, `docx`, `url` 등 다양한 입력을 텍스트로 변환하는 기능만 담당           |


2. 처리 가능한 형식

| 유형      | 설명        | 파서 함수                      |
| ------- | --------- | -------------------------- |
| `.txt`  | 일반 텍스트 파일 | `extract_text_from_txt()`  |
| `.pdf`  | PDF 문서    | `extract_text_from_pdf()`  |
| `.docx` | Word 문서   | `extract_text_from_docx()` |
| `url`   | 웹 URL 내용  | `extract_text_from_url()`  |

3. 소스 코드 정리 
  - `src/volumns/fastapi/utils/parse_document.py` 생성
  - `doc_service.py` 수정
  - `doc_router.py` 수정

4. `requirements.txt` - 문서 파싱용 추가 필수 라이브러리 추가
  - 파일 수정
  - docker compose 재시작


5. 테스트
```bash
# SWAGGER-UI 확인 재기동 확인용
curl http://localhost:48001/docs

# 파일 업로드(.txt, .pdf, .docx) 테스트
curl -X POST "http://localhost:48001/documents/upload-doc" \
  -F "file=@/labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/test_doc.txt"
curl -X POST "http://localhost:48001/documents/upload-doc" \
  -F "file=@/labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/DETAILS_OF_TASKS_20250628.pdf"

# URL 업로드 (웹 페이지 텍스트 크롤링)
curl -X POST "http://localhost:48001/documents/upload-doc?url=https://en.wikipedia.org/wiki/Retrieval-augmented_generation"

# 파일 업로드 목록 확인
curl -X GET http://localhost:48001/documents
```

---

## 9. MongoDB 로그 서버 구현

### 1) MongoDB 서버 실행 (Docker 기반)

1. `/labs/docker/images/chat-dev-sjchoi/src/images/mongodb/docker-compose.yml` 생성

2. 위 파일 존재하는 폴더에서 도커 실행 명령어
```bash
cd src/images/mongodb
docker-compose up -d mongodb mongo-express
```

3. 실행 확인
```bash
# 1. MongoDB 컨테이너 상태 확인
docker ps | grep mongo

# 2. MongoDB CLI 접속 (bash에서 직접 확인 / 컨테이너명 확인 필수)
docker exec -it mongodb-sjchoi mongosh
# mongosh 또는 mongo 명령어로 접속
## 현재 DB 목록 보기
> show dbs
## 컬렉션 목록 확인
> use rag_chatbot       # 아직 안만든 상태면 자동 생성으로 'switched to db rag_chatbot' 가 뜸
> show collections      # 아직 아무것도 안 넣은 상태면 빈줄
## 로그 데이터 조회
> db.llm_logs.find().sort({ created_at: -1 }).limit(3).pretty()
## 로그 수 개수 확인
> db.llm_logs.countDocuments()
```

### 2) MongoDB 연결 설정

1. fastAPI 수정
  - `requirements.txt` - motor 추가
  - `.env` - MONGO_URL 추가
  - `db/mongodb.py` - 파일 생성

2. fastAPI 도커 재실행
```bash
docker-compose down
docker-compose up -d --build
```


### 3) 로그 저장 기능 구현

1. `services/log_serice.py` - 파일 생성
2. `services/llm_service.py` - call_llm_with_timing 메소드 추가
3. `services/chat_service.py` - call_llm -> call_llm_with_timing 변경, log_llm_response 사용 추가


### 4) 테스트 및 구현 확인

1. log 데이터 쌓기
```bash
# /chat
curl -X POST http://localhost:48001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "한국의 수도는?", "history": []}'

# /chat-session
curl -X POST http://localhost:48001/chat-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user0001", "session_id": "session0001", "query": "서울은 어디에 있어?"}'
curl -X POST http://localhost:48001/chat-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user0001", "session_id": "session0001", "query": "부산과의 거리는 얼마나 돼?"}'
```

2. log 확인
```bash
# 도커 서버 접속 (컨테이너명 확인 필수)
docker exec -it mongodb-sjchoi mongosh
# Mongo DB 명령어
> use rag_chatbot
> db.llm_logs.find().sort({ created_at: -1 }).pretty()
```

---

## 10. LLM 응답 시간 및 context 길이 로깅

1. call_llm_with_logging() 함수 작성
  → LLM 호출 + 소요 시간 측정 + MongoDB 로그 저장을 하나의 함수로 통합
  - chat_with_context(), chat_with_session()에서 기존 LLM 호출 → call_llm_with_logging()으로 교체

2. 예외 발생 시: call_llm_with_logging() 함수에서 처리
 - 에러 메시지를 answer로 반환
 - is_error, error_type, error_message 필드까지 함께 로그 저장
 - 정상/오류 로그 모두 MongoDB llm_logs 컬렉션에 저장됨

3. log_llm_response() 확장:
  - LLM 호출을 래핑하여 다음 항목을 기록
    * 응답 소요 시간 (response_time)
    * 요청 ID (request_id)
    * 요청 시각 (request_at)
    * user_id / session_id: 사용자 세션 정보
    * status_code: 성공(200), 실패 시 오류 코드
    * is_error, error_type, error_message: 예외 여부 및 상세 정보
    * parameter_setting: 사용한 파라미터 (예: temperature, max_tokens)
    * prompt_tokens, completion_tokens, total_tokens: 사용한 토큰 수 (vLLM 응답에서 추출)
  - 확장된 저장 필드
```python
{
  "query": ...,               # 사용자 입력
  "response": ...,            # LLM 응답
  "response_time": ...,       # 처리 시간 (초)
  "context": ...,             # 전체 프롬프트
  "user_id": ...,             # 사용자 ID
  "session_id": ...,          # 세션 ID
  "status_code": ...,         # HTTP 상태 코드
  "is_error": ...,            # 오류 여부
  "error_type": ...,          # 오류 종류
  "error_message": ...,       # 오류 메시지
  "request_id": ...,          # 고유 요청 ID
  "request_at": ...,          # 요청 시간
  "parameter_setting": ...,   # 모델 호출 파라미터
  "prompt_tokens": ...,       # 입력 토큰 수
  "completion_tokens": ...,   # 출력 토큰 수
  "total_tokens": ...         # 전체 토큰 수
}

```

4. 로그 확인
2. log 확인
```bash
# 도커 서버 접속 (컨테이너명 확인 필수)
docker exec -it mongodb-sjchoi mongosh
# Mongo DB 명령어
> use rag_chatbot
# 가장 최근 로그 1개만 보기
> db.llm_logs.find().sort({ created_at: -1 }).limit(1).pretty()
```

---

## 11. 대화 요약 기능 추가

* 처리 변경
1. chat_with_summary() 요청
2. 세션 요약 정보 검색
3. 벡터 검색 search_similar_docs
4. build_prompt
5. call_llm_with_logging
6. 세션저장
    save_message(user_id, session_id, {"role": "user", "content": query})
    save_message(user_id, session_id, {"role": "assistant", "content": answer})
7. 결과 리턴
8. 응답 후 요약 작업 백그라운드에서 실행


* 전체 흐름 정리

```bash
[ FastAPI ]
1. POST /chat_session
 └─ 2. get_session_summary(session_id)  → summary 정보 포함
 └─ 3. search_similar_docs(query)
 └─ 4. build_prompt(query, docs, history or summary)
 └─ 5. call_llm_with_logging(...)
 └─ 6. save_message(...)
 └─ 7. return answer + docs
```

1. `chat_service.py`
  - summarize_messages() 함수 추가
  - summarize_and_update_session() 함수 추가

2. `session_service.py`
  - update_session_summary 함수 추가
  - get_session_summary 함수 추가

3. `chat_router.py`(@router.post("/chat-session"))
  - 응답 후 요약 작업 백그라운드에서 실행
  - background_tasks.add_task(summarize_and_update_session)

4. 요약 정보로 chat : (@router.post("/chat-session")) 추가
  - `chat_router.py` chat_summary 함수 추가
  - `chat_service.py`chat_with_summary 함수 추가

5. 테스트
```bash
# /chat-session
curl -X POST http://localhost:48001/chat-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user0001", "session_id": "session0001", "query": "인천에서 유명한 관광지 소개해줘"}'

# log 에서 summary 확인

# /chat-summary
curl -X POST http://localhost:48001/chat-summary \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user0001", "session_id": "session0001", "query": "부산은 어떄?"}'
```








----

* 추가 작업 고려 내용

1) prompt 분리 - DB 에서 prompt_id 로 데이터 가져오기
2) setting 값 DB 에서 관리


* 추가 로깅 항목
1) search_similar_docs 소요 시간
2) prompt_id
3) 