# services/checkpoint_service.py
"""
CheckpointService

Singleton service that provides LangGraph SQLite checkpointer integration.

Notes:
- The LangGraph SqliteSaver is an optional dependency. Import it lazily so
  the application can still import this module even if langgraph is not installed.
- If the application tries to obtain a checkpointer and langgraph is missing,
  we raise a clear ChatBotException with actionable installation instructions.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from config.config import settings
from core.exception import ChatBotException
from core.logger import logger

# We import SqliteSaver lazily in get_checkpointer() to avoid hard
# dependency at import-time (which makes the whole app fail if langgraph isn't installed).
_SqliteSaverType = None  # type: ignore


class CheckpointService:
    """
    Singleton service for LangGraph SQLite checkpoints.
    """

    _connection: Optional[sqlite3.Connection] = None
    _checkpointer = None

    @classmethod
    def _ensure_sqlitesaver_available(cls):
        """
        Attempt to import the LangGraph SqliteSaver. Raise ChatBotException with
        instructions if not available.
        """
        global _SqliteSaverType
        if _SqliteSaverType is not None:
            return

        try:
            # Import lazily
            mod = __import__("langgraph.checkpoint.sqlite", fromlist=["SqliteSaver"])
            _SqliteSaverType = getattr(mod, "SqliteSaver")
        except Exception as e:
            # Provide actionable message
            raise ChatBotException(
                RuntimeError(
                    "LangGraph SqliteSaver is not available. "
                    "If you want to use LangGraph checkpointing, please install the 'langgraph' package "
                    "that provides the checkpoint backend. For example:\n\n"
                    "    pip install langgraph\n\n"
                    "Or, if the project uses a particular installation method, follow its README for installation.\n\n"
                    f"Original import error: {e}"
                )
            ) from e

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
        Return a LangGraph SqliteSaver checkpointer instance.

        This method lazily imports the required LangGraph SqliteSaver class
        and constructs a checkpointer bound to the module's SQLite connection.
        """
        try:
            if cls._checkpointer is None:
                # Ensure the SqliteSaver type is available (lazily import)
                cls._ensure_sqlitesaver_available()

                # Construct SqliteSaver using the sqlite connection
                logger.info("Initializing LangGraph Checkpointer...")
                cls._checkpointer = _SqliteSaverType(conn=cls.get_connection())
                logger.info("Checkpointer initialized successfully.")

            return cls._checkpointer
        except ChatBotException:
            # Re-raise ChatBotException raised by _ensure_sqlitesaver_available
            raise
        except Exception as e:
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

        This relies on the underlying SqliteSaver providing a list(None) method
        that enumerates checkpoints. If langgraph is not installed, this will raise
        a ChatBotException with instructions.
        """
        try:
            checkpointer = cls.get_checkpointer()
            thread_ids = set()

            # The SqliteSaver API exposes list(checkpoint_key_or_none)
            for checkpoint in checkpointer.list(None):
                # Many checkpointer configs store thread_id under configurable keys
                cfg = checkpoint.config if isinstance(checkpoint, dict) else getattr(checkpoint, "config", {})
                # Best-effort extraction
                thread_id = (
                    cfg.get("configurable", {}).get("thread_id")
                    or cfg.get("configurable", {}).get("thread")
                    or cfg.get("thread_id")
                    or (checkpoint.config["configurable"]["thread_id"] if "configurable" in cfg and "thread_id" in cfg["configurable"] else None)
                )
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
        return {"database": getattr(settings, "CHECKPOINT_DB_PATH", "data/checkpoints/checkpoints.db"), "backend": "LangGraph-SQLite"}

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
            return thread_id in cls.list_threads()
        except Exception as e:
            raise ChatBotException(e)