6/27-29 RAG 사용하는 챗봇 만글기

| 단계 | 작업 내용                        | 도구/기술                  |
| -- | ---------------------------- | ---------------------- |
| 1  | `docker-compose`로 vLLM 실행    | vLLM, gemma            |
| 2  | 문서 → embedding → DB 저장 기능 구현 | BGE-m3-ko + ChromaDB   |
| 3  | 질문 → 검색 → 답변 생성              | RAG 파이프라인              |
| 4  | 세션 관리 기능 구현                  | Redis                  |
| 5  | FastAPI 서버 통합                | API 라우터 구성             |
| 6  | 테스트 및 튜닝                     | curl/Postman or Web UI |

-----

## 1. vLLM docker-compose 로 구성하기

### 1) docker-compose 생성 및 실행

#### docker-compose.yml 생성

`/src/images/vllm/docker-compose.yml`

#### 실행 명령

```bash
cd src/images/vllm
docker compose up -d
```

#### 테스트 (모델 로딩 확인)

``` bash
curl http://localhost:48000/v1/models
```
```bash
# 로그 확인 명령어
docker logs vllm-server-sjchoi --tail 100
```

##### 모델 로딩 완료 확인을 위한 로그 모니터링

```bash
docker logs -f vllm-server-sjchoi
```

→ 로딩이 끝나면 아래와 비슷한 로그가 출력됩니다:
```plaintext
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 2. 2단계: fastAPI


### 2_1. docker-compose 실행 및 문서 임베딩(임시) → 벡터 DB(ChromaDB) 저장 기본 코드 작성

#### 1) 소스코드

##### 항목

| 항목        | 구성                                       |
| --------- | ---------------------------------------- |
| 임베딩 모델    | `BGE-m3-ko` (HuggingFace)                |
| 벡터 DB     | `ChromaDB` (Python 기반 로컬 DB)             |
| 인터페이스     | FastAPI (문서 업로드 + 임베딩 트리거)               |
| Docker 경로 | `/src/images/fastapi/docker-compose.yml` |
| 소스코드      | `/src/volumns/fastapi` 안에 구성             |


##### 디렉토리 구성

```css
/src/volumns/fastapi
├── app/
│   ├── main.py             ← FastAPI 진입점
│   ├── embed.py            ← 문서 분할 + 임베딩
│   ├── chroma_db.py        ← ChromaDB 연결
│   └── model_loader.py     ← BGE-m3-ko 로딩
└── requirements.txt        ← transformers + chromadb 등
```
```bash
# 파일/디렉토리 생성 명령어
mkdir -p volumns/fastapi/app

touch volumns/fastapi/app/main.py
touch volumns/fastapi/app/embed.py
touch volumns/fastapi/app/chroma_db.py
touch volumns/fastapi/app/model_loader.py
touch volumns/fastapi/requirements.txt
```

#### 2) docker-compose 생성 및 실행

##### docker-compose.yml + Dockerfile 생성

`/src/images/fastapi/docker-compose.yml`
`/src/images/fastapi/Dockerfile`

##### 실행 명령

```bash
cd src/images/fastapi
docker compose up --build -d        # --build 는 한번만 실행
```

✅ 언제만 --build가 필요하냐면?
- 처음 이미지를 만들 때
- requirements.txt를 수정한 경우
- Dockerfile을 수정한 경우

##### 테스트

1) Swagger UI 확인
```bash
curl http://localhost:48001/docs
```
2) 테스트 파일 생성 및 실행
```bash
echo "이것은 테스트 문서입니다." > /labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/test_doc.txt
```
```bash
curl -X POST -F "file=@/labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/test_doc.txt" http://localhost:48001/upload-doc
```

---

### 2_2. 임베딩 모델 붙이기: BGE-m3-ko

#### 임베딩 모델

`/labs/docker/volumes/ml-dev/share/model/BGE-m3-ko` 경로에 다운로드해둔 모델 사용

```bash
# docker-compose.yml 을 비롯한 소스코드 수정 후 테스트
cd /labs/docker/images/chat-dev-sjchoi/src/images/fastapi
docker compose down
docker compose up --build -d  # ← requirements.txt 수정 시 반드시 --build
```

### 2_3. 질문 기반 검색 API 만들기

#### 새로운 API 엔드포인트 추가

- POST /search-doc
- 입력: JSON { "query": "질문 내용" }
- 출력: 관련 문서 리스트

1. `search_doc.py` 모듈 생성
```bash
touch volumns/fastapi/app/search_doc.py
```
2. `search_doc.py` 에 search_similar_docs 함수 생성
3. `main.py` 에 API 추가
4. 테스트
```bash
curl -X POST http://localhost:48001/search-doc \
     -H "Content-Type: application/json" \
     -d '{"query": "테스트 문서의 내용은?"}'
```

✅ 만약 결과값이 없는 경우, 저장된 벡터값이 없어서일 수 있으므로 새로이 벡터값 저장해두기
```bash
curl -X POST -F "file=@/labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/test_doc.txt" http://localhost:48001/upload-doc
```


### 2_4. ChromaDB 파이프라인에 파일명 기반 메타데이터 저장 추가 

1. `main.py` 수정 (파일명 전달)
2. `embed.py` 수정 (metadata 저장)
3. 테스트
```bash
curl -X POST -F "file=@/labs/docker/images/chat-dev-sjchoi/src/volumns/fastapi/test_doc.txt" http://localhost:48001/upload-doc
```

---

## 3. RAG 파이프라인
### 3_1. 세션 기반 질문-응답 API 구성 (LLM 호출 포함)
 
1. `app/services/chat_service.py` 추가
```bash
touch volumns/fastapi/app/services/chat_service.py
```
2. `main.py` 수정
3. `llm_servcie.py` 추가
```bash
touch volumns/fastapi/app/services/llm_servcie.py
```
4. 테스트
```bash
curl -X POST http://localhost:48001/chat \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": "test-session-001",
        "query": "테스트 문서에 대해 알려줘",
        "top_k": 2
      }'
```

### 3_2. LLM 서버 연동 (vLLM)

#### 1) LLM 서버 연동

1. 공통 네트워크 만들기 (한 번만 실행)

> 다른 docker-compose.yml을 통해 서버 관리하기 위해서
> FastAPI와 vLLM 컨테이너를 동일한 Docker 네트워크에 수동으로 연결

```bash
docker network create rag-net
```

2. 각 docker-compose.yml에서 네트워크 명시

✅ FastAPI - /src/images/fastapi/docker-compose.yml
```yaml
services:
  fastapi:
    ...
    networks:
      - rag-net

networks:
  rag-net:
    external: true
```
✅ vLLM - /src/images/vllm/docker-compose.yml
```yaml
services:
  vllm:
    ...
    networks:
      - rag-net

networks:
  rag-net:
    external: true
```

3. vLLM 서버 실행 확인
```bash
curl http://localhost:48000/v1/models
# 정상일 경우 결과: {"data": [{"id": "gemma-3-12b-it", "object": "model", ...}]}
```

4. .env 파일에 vLLM 주소 설정

5. 도커 재실행
```bash
cd /labs/docker/images/chat-dev-sjchoi/src/images/fastapi
docker compose build
docker compose up -d
```
```bash
cd /labs/docker/images/chat-dev-sjchoi/src/images/vllm
docker compose down
docker compose up -d
```

6. vLLM 서버 접속 확인을 위한 "/llm-status" API 추가
    - `llm_service.py`
    - `chat_service.py`
    - `main.py`

7. 테스트
```bash
curl http://localhost:48001/llm-status
# 성공: {"status":"ok","message":"LLM 서버 연결 성공"}
# 실패: {"detail":"LLM 서버에 연결할 수 없습니다."}
```

8. 실제 모델 정보 확인용 `/llm-status/detail` API 확장
    - `llm_service.py`
    - `chat_service.py`
    - `main.py`

9. 테스트
```bash
curl http://localhost:48001/llm-status/detail
```

#### 2) LLM을 통해 결과받기

1. `requirements.txt` 수정 => requests 추가
변경 후 docker-compose build 필요
```
cd /labs/docker/images/chat-dev-sjchoi/src/images/fastapi
docker compose build
docker compose up -d
```

2. `llm_service.py` 의 call_llm() 메소드 수정
- `.env` 파일 : DEFAULT_MODEL 등록

4. 테스트
```
curl -X POST http://localhost:48001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "테스트 문서에 대해 알려줘", "history": []}'
```


### 3_3. 대화 흐름(세션) 관리