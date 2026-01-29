from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    chroma_dir: str = os.getenv("CHROMA_DIR", "./chroma_db_v2")
    collection_name: str = os.getenv("COLLECTION_NAME", "portfolio_docs")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    top_k: int = int(os.getenv("TOP_K", 6))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 900))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 150))
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", 12000)) 

settings = Settings()

   