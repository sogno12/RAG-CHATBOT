import os
from motor.motor_asyncio import AsyncIOMotorClient

# 환경 변수에서 MongoDB URL 가져오기
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
mongo_client = AsyncIOMotorClient(MONGO_URL)

db = mongo_client["rag_chatbot"]
