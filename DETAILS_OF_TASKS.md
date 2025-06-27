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