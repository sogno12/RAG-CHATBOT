from chromadb import Client
from chromadb.config import Settings

def get_chroma_client():
    return Client(Settings(
        persist_directory="./chroma_db"
    ))
