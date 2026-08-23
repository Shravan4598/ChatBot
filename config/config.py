# config/config.py
"""
Configuration module for the AI ChatBot project.

- Loads environment variables from a .env file (using python-dotenv).
- Exposes a Settings dataclass that holds configuration values parsed safely.
- Avoids printing secret values; logs that configuration loaded successfully.
"""

from dataclasses import dataclass
import os
from dotenv import load_dotenv
from core.logger import logger

# Load .env from project root (this will silently succeed if there's no .env)
load_dotenv()

def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")

def _parse_int(value: str, default: int) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def _parse_float(value: str, default: float) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

@dataclass
class Settings:
    # LLM / Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Langsmith / LangGraph
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "ChatBot")
    LANGSMITH_TRACKING: bool = _parse_bool(os.getenv("LANGSMITH_TRACKING", "true"))

    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

    # External APIs (weather/finance)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    ALPHAVANTAGE_API_KEY: str = os.getenv("ALPHAVANTAGE_API_KEY", "")

    # Embeddings / Vector DB
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_DB: str = os.getenv("VECTOR_DB", "faiss")  # "faiss", "chroma", "milvus", etc.
    VECTOR_STORE_DIR: str = os.getenv("VECTOR_STORE_DIR", "data/vectorstore")
    DOCS_DIR: str = os.getenv("DOCS_DIR", "data/uploads")

    # LLM runtime hyperparameters
    LLM_TEMPERATURE: float = _parse_float(os.getenv("LLM_TEMPERATURE", None), 0.3)
    MAX_OUTPUT_TOKENS: int = _parse_int(os.getenv("MAX_OUTPUT_TOKENS", None), 2048)
    REQUEST_TIMEOUT: int = _parse_int(os.getenv("REQUEST_TIMEOUT", None), 30)

    # Chunking / ingestion
    CHUNK_SIZE: int = _parse_int(os.getenv("CHUNK_SIZE", None), 1000)
    CHUNK_OVERLAP: int = _parse_int(os.getenv("CHUNK_OVERLAP", None), 200)

    # Streamlit / UI
    PAGE_TITLE: str = os.getenv("PAGE_TITLE", "AI ChatBot")
    PAGE_ICON: str = os.getenv("PAGE_ICON", "🤖")

    # Misc
    LOG_ROOT: str = os.getenv("LOG_ROOT", "logs")
    REQUESTS_PER_MINUTE: int = _parse_int(os.getenv("REQUESTS_PER_MINUTE", None), 60)

# Instantiate a settings object that can be imported elsewhere:
settings = Settings()

# Log configuration loaded (do not log secret values)
masked_gemini = "<set>" if bool(settings.GEMINI_API_KEY) else "<not set>"
logger.info(f"Configuration loaded. Gemini key present: {masked_gemini}. Vector DB: {settings.VECTOR_DB}. Langsmith: {'set' if settings.LANGSMITH_API_KEY else 'not-set'}.")