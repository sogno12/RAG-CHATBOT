# src/images/fastapi/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY src/volumns/fastapi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/volumns/fastapi/app ./app
