"""
Configuration module for the AI ChatBot.

Loads environment variables from a .env file and provides
a centralized Settings object that can be imported
throughout the application.
"""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

from core.logger import logger

# ------------------------------------------------------------------
# Load Environment Variables
# ------------------------------------------------------------------

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Application configuration settings.
    """

    # =========================
    # Google Gemini
    # =========================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # =========================
    # LangSmith
    # =========================
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv(
        "LANGSMITH_PROJECT",
        "AI-ChatBot",
    )
    LANGSMITH_TRACING: str = os.getenv(
        "LANGSMITH_TRACING",
        "true",
    )
    LANGSMITH_ENDPOINT: str = os.getenv(
        "LANGSMITH_ENDPOINT",
        "https://api.smith.langchain.com",
    )

    # =========================
    # Weather API
    # =========================
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")

    # =========================
    # Embeddings
    # =========================
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    # =========================
    # Vector Database
    # =========================
    VECTOR_DB: str = os.getenv("VECTOR_DB", "faiss")

    VECTOR_STORE_PATH: str = os.getenv(
        "VECTOR_STORE_PATH",
        "data/vectorstore",
    )

    # =========================
    # Uploaded Documents
    # =========================
    UPLOAD_DIRECTORY = "data/uploads"
    DOCUMENT_PATH: str = os.getenv(
        "DOCUMENT_PATH",
        "data/uploads",
    )

    # =========================
    # LLM Parameters
    # =========================
    TEMPERATURE: float = float(
        os.getenv("TEMPERATURE", "0.3")
    )

    MAX_OUTPUT_TOKENS: int = int(
        os.getenv("MAX_OUTPUT_TOKENS", "2048")
    )

    # =========================
    # Chunking
    # =========================
    CHUNK_SIZE: int = int(
        os.getenv("CHUNK_SIZE", "1000")
    )

    CHUNK_OVERLAP: int = int(
        os.getenv("CHUNK_OVERLAP", "200")
    )

    # =========================
    # Streamlit
    # =========================
    PAGE_TITLE: str = "AI ChatBot"

    PAGE_ICON: str = "🤖"


settings = Settings()

logger.info("Configuration loaded successfully.")