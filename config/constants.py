# config/constants.py
"""
Application-wide constants and default paths.
Keep this file simple and import-safe.
"""

from pathlib import Path
import os

# Project information
PROJECT_NAME = "ChatBot"
PROJECT_VERSION = "1.0.0"

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Document storage
DOCS_DIR = DATA_DIR / "uploads"
VECTOR_STORE_DIR = DATA_DIR / "vectorstore"

# Supported document extensions for ingestion
SUPPORTED_DOC_EXTENSIONS = {".pdf", ".txt", ".docx", ".md", ".pptx"}

# Default vector store options
VECTOR_STORES = ("faiss", "chroma", "milvus")

# Default embedding models
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Default LLMs / tools names (used as keys in registries)
TOOL_CHAT = "chat"
TOOL_RAG = "rag"
TOOL_SEARCH = "search"
TOOL_WEATHER = "weather"
TOOL_STOCKS = "stocks"
TOOL_YOUTUBE = "youtube"

# Message/session constants
SESSION_MESSAGES = "messages"
SESSION_HISTORY_KEY = "chat_history"

# File upload allowed list (same as extensions but explicit)
ALLOWED_UPLOAD_SUFFIXES = tuple(SUPPORTED_DOC_EXTENSIONS)

# Timeouts and default values
DEFAULT_REQUEST_TIMEOUT = 30  # seconds
DEFAULT_MAX_TOKENS = 2048

# Encoding & IO
ENCODING = "utf-8"

# Ensure directories exist when imported (safe to call)
for p in (DATA_DIR, LOGS_DIR, DOCS_DIR, VECTOR_STORE_DIR):
    try:
        os.makedirs(p, exist_ok=True)
    except Exception:
        # If the environment does not allow creation at import-time, skip silently.
        pass