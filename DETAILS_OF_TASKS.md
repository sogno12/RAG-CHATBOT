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


### 1) docker-compose 실행 및 문서 임베딩(임시) → 벡터 DB(ChromaDB) 저장 기본 코드 작성

### 1_1) 소스코드

#### 항목

| 항목        | 구성                                       |
| --------- | ---------------------------------------- |
| 임베딩 모델    | `BGE-m3-ko` (HuggingFace)                |
| 벡터 DB     | `ChromaDB` (Python 기반 로컬 DB)             |
| 인터페이스     | FastAPI (문서 업로드 + 임베딩 트리거)               |
| Docker 경로 | `/src/images/fastapi/docker-compose.yml` |
| 소스코드      | `/src/volumns/fastapi` 안에 구성             |


#### 디렉토리 구성

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

### 2_1) docker-compose 생성 및 실행

#### docker-compose.yml + Dockerfile 생성

`/src/images/fastapi/docker-compose.yml`
`/src/images/fastapi/Dockerfile`

#### 실행 명령

```bash
cd src/images/fastapi
docker compose up --build -d        # --build 는 한번만 실행
```

✅ 언제만 --build가 필요하냐면?
- 처음 이미지를 만들 때
- requirements.txt를 수정한 경우
- Dockerfile을 수정한 경우

#### 테스트

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


