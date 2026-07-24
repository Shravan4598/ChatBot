"""
constants.py

This module contains all application-wide constants used throughout
the AI ChatBot project.

Keeping constants in one place improves maintainability and
avoids hardcoding values across multiple modules.
"""

from pathlib import Path

# =============================================================================
# PROJECT INFORMATION
# =============================================================================

PROJECT_NAME: str = "Production AI ChatBot"
PROJECT_VERSION: str = "1.0.0"

# =============================================================================
# DIRECTORY PATHS
# =============================================================================

BASE_DIR = Path.cwd()

DATA_DIR = BASE_DIR / "data"

UPLOAD_DIR = DATA_DIR / "uploads"

VECTOR_STORE_DIR = DATA_DIR / "vectorstore"

LOG_DIR = BASE_DIR / "logs"

# =============================================================================
# SUPPORTED DOCUMENT TYPES
# =============================================================================

SUPPORTED_DOCUMENTS = [
    ".pdf",
    ".txt",
    ".docx",
]

# =============================================================================
# VECTOR DATABASES
# =============================================================================

FAISS = "faiss"
CHROMA = "chroma"

SUPPORTED_VECTOR_STORES = [
    FAISS,
    CHROMA,
]

# =============================================================================
# EMBEDDING MODELS
# =============================================================================

DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

# =============================================================================
# GEMINI MODELS
# =============================================================================

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# =============================================================================
# LANGGRAPH NODES
# =============================================================================

ROUTER_NODE = "router"

CHAT_NODE = "chat"

RAG_NODE = "rag"

SEARCH_NODE = "search"

WEATHER_NODE = "weather"

STOCK_NODE = "stock"

YOUTUBE_NODE = "youtube"

FINAL_NODE = "final"

# =============================================================================
# TOOL NAMES
# =============================================================================

CHAT_TOOL = "chat"

RAG_TOOL = "rag"

SEARCH_TOOL = "duckduckgo"

WEATHER_TOOL = "weather"

STOCK_TOOL = "stock"

YOUTUBE_TOOL = "youtube"

# =============================================================================
# STREAMLIT SESSION KEYS
# =============================================================================

SESSION_MESSAGES = "messages"

SESSION_CHAT_HISTORY = "chat_history"

SESSION_VECTORSTORE = "vectorstore"

SESSION_UPLOADED_FILES = "uploaded_files"

SESSION_GRAPH = "graph"

# =============================================================================
# RAG DEFAULTS
# =============================================================================

DEFAULT_CHUNK_SIZE = 1000

DEFAULT_CHUNK_OVERLAP = 200

TOP_K_RESULTS = 4

# =============================================================================
# LLM DEFAULTS
# =============================================================================

DEFAULT_TEMPERATURE = 0.3

DEFAULT_MAX_OUTPUT_TOKENS = 2048

# =============================================================================
# CHATBOT SYSTEM MESSAGE
# =============================================================================

DEFAULT_SYSTEM_ROLE = (
    "You are a helpful AI assistant."
)

# =============================================================================
# WEATHER
# =============================================================================

DEFAULT_WEATHER_UNIT = "metric"

# =============================================================================
# UI
# =============================================================================

PAGE_TITLE = "AI ChatBot"

PAGE_ICON = "🤖"

SIDEBAR_TITLE = "AI ChatBot"

WELCOME_MESSAGE = (
    "Hello! How can I help you today?"
)

# =============================================================================
# MISC
# =============================================================================

ENCODING = "utf-8"

REQUEST_TIMEOUT = 30