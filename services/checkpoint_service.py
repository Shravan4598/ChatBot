# services/checkpoint_service.py
"""
CheckpointService

Singleton service that provides LangGraph SQLite checkpointer integration.

This implementation is defensive:
- It attempts a lazy import of the LangGraph SqliteSaver.
- If the class is not available, get_checkpointer() returns None instead of raising,
  so the rest of the application can continue to run without checkpointing.
- Methods that require a checkpointer will raise ChatBotException only when they're
  actually invoked and the checkpointer is missing.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from config.config import settings
from core.exception import ChatBotException
from core.logger import logger

_SqliteSaverType = None  # lazily populated if available


class CheckpointService:
    """
    Singleton service for LangGraph SQLite checkpoints.
    """

    _connection: Optional[sqlite3.Connection] = None
    _checkpointer = None

    @classmethod
    def _try_import_sqlitesaver(cls) -> bool:
        """
        Attempt to import LangGraph SqliteSaver lazily.
        Returns True if available, False otherwise.
        Does not raise — logs the reason on failure.
        """
        global _SqliteSaverType
        if _SqliteSaverType is not None:
            return True

        try:
            mod = __import__("langgraph.checkpoint.sqlite", fromlist=["SqliteSaver"])
            _SqliteSaverType = getattr(mod, "SqliteSaver")
            return True
        except Exception as e:
            logger.debug("LangGraph SqliteSaver not available: %s", e)
            _SqliteSaverType = None
            return False

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """
        Return SQLite connection (singleton). The DB path defaults to settings.CHECKPOINT_DB_PATH
        or data/checkpoints/checkpoints.db if not set.
        """
        try:
            if cls._connection is None:
                db_path_str = getattr(settings, "CHECKPOINT_DB_PATH", None)
                if not db_path_str:
                    db_path_str = "data/checkpoints/checkpoints.db"
                db_path = Path(db_path_str)
                db_path.parent.mkdir(parents=True, exist_ok=True)

                logger.info("Creating SQLite connection: %s", db_path)

                cls._connection = sqlite3.connect(database=str(db_path), check_same_thread=False)

            return cls._connection
        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================

    @classmethod
    def get_checkpointer(cls):
        """
        Return a LangGraph SqliteSaver checkpointer instance or None if unavailable.

        This method will NOT raise if the LangGraph SqliteSaver is not present.
        It will return None, allowing callers to continue without checkpointing.
        """
        try:
            if cls._checkpointer is not None:
                return cls._checkpointer

            if not cls._try_import_sqlitesaver():
                # Not available — do not raise here, allow caller to decide behavior
                logger.info("LangGraph SqliteSaver not available; checkpointing disabled.")
                return None

            # Construct SqliteSaver using the sqlite connection
            logger.info("Initializing LangGraph Checkpointer...")
            cls._checkpointer = _SqliteSaverType(conn=cls.get_connection())
            logger.info("Checkpointer initialized successfully.")
            return cls._checkpointer

        except Exception as e:
            # If unexpected error occurs while creating checkpointer, wrap and raise.
            raise ChatBotException(e)

    # ==============================================================

    @classmethod
    def close(cls) -> None:
        """
        Close SQLite connection and reset checkpointer.
        """
        try:
            if cls._connection:
                cls._connection.close()
                cls._connection = None
                cls._checkpointer = None
                logger.info("Checkpoint connection closed.")
        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================

    @classmethod
    def list_threads(cls) -> list[str]:
        """
        Return all stored thread IDs.

        If the checkpointer is not available, raise ChatBotException indicating checkpointing is disabled.
        """
        try:
            checkpointer = cls.get_checkpointer()
            if checkpointer is None:
                raise ChatBotException(RuntimeError("Checkpointing is not available. Install langgraph to enable checkpoints."))

            thread_ids = set()
            for checkpoint in checkpointer.list(None):
                cfg = checkpoint.config if isinstance(checkpoint, dict) else getattr(checkpoint, "config", {})
                # Best-effort extraction of thread_id
                thread_id = None
                if isinstance(cfg, dict):
                    thread_id = cfg.get("configurable", {}).get("thread_id") or cfg.get("thread_id")
                if not thread_id:
                    # try attribute access
                    thread_id = getattr(checkpoint, "task_id", None) or getattr(checkpoint, "thread_id", None)
                if thread_id:
                    thread_ids.add(thread_id)
            return sorted(thread_ids)

        except ChatBotException:
            raise
        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================

    @classmethod
    def info(cls) -> dict:
        """
        Return checkpoint configuration info.
        """
        return {"database": getattr(settings, "CHECKPOINT_DB_PATH", "data/checkpoints/checkpoints.db"), "backend": "LangGraph-SQLite" if cls._try_import_sqlitesaver() else "None"}

    # ==============================================================

    @classmethod
    def connection(cls) -> sqlite3.Connection:
        """
        Alias for get_connection().
        """
        return cls.get_connection()

    # ==============================================================

    @classmethod
    def thread_exists(cls, thread_id: str) -> bool:
        """
        Check whether checkpoints exist for a thread.
        """
        try:
            checkpointer = cls.get_checkpointer()
            if checkpointer is None:
                raise ChatBotException(RuntimeError("Checkpointing is not available. Install langgraph to enable checkpoints."))
            return thread_id in cls.list_threads()
        except ChatBotException:
            raise
        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================

    @classmethod
    def ping(cls) -> bool:
        """
        Simple health check for checkpointing. Returns True if checkpointer available.
        """
        try:
            return cls.get_checkpointer() is not None
        except Exception:
            return False