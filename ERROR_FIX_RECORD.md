
* 문제 발생 및 해결


문제_1. 원격 Docker 데몬(ssh://redsoft@192.168.0.251)에 연결을 시도하다가 실패

```bash
# 에러 메세지
unable to get image 'fastapi-fastapi': error during connect: Get "http://docker.example.com/v1.47/images/fastapi-fastapi/json": command [ssh -o ConnectTimeout=30 -T -l redsoft -- 192.168.0.251 docker system dial-stdio] has exited with exit status 255, make sure the URL is valid, and Docker 18.09 or later is installed on the remote host: stderr=ssh: connect to host 192.168.0.251 port 22: Connection timed out

# 주요 에러 메세지
ssh: connect to host 192.168.0.251 port 22: Connection timed out
```
* 원인:
  - DOCKER_HOST=ssh://redsoft@192.168.0.251 환경 변수로 인해 Docker 명령이 모두 원격 서버로 전송되고 있음
  - 하지만 SSH 연결이 불가능하여 Docker 자체가 동작하지 않음

* 해결: 로컬 Docker로 전환 (일시적)
  - 일시적으로 DOCKER_HOST 해제
  - 이 방법은 현재 쉘 세션에만 적용
```bash
unset DOCKER_HOST ## <<-- 요거 실행이 중요함

# 이후에 하려던 docker 작업 진행
docker-compose down
docker-compose up -d --build
```