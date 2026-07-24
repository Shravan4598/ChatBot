"""
services/checkpoint_service.py

Centralized LangGraph Checkpoint Service.

Responsibilities
----------------
- Create SQLite connection
- Initialize LangGraph SqliteSaver
- Reuse a single checkpoint instance
- Provide thread-safe checkpoint access
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from langgraph.checkpoint.sqlite import SqliteSaver

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging


class CheckpointService:
    """
    Singleton service for LangGraph SQLite checkpoints.
    """

    _connection: Optional[sqlite3.Connection] = None
    _checkpointer: Optional[SqliteSaver] = None

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """
        Return SQLite connection.
        """

        try:

            if cls._connection is None:

                db_path = Path(settings.CHECKPOINT_DB_PATH)

                db_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                logging.info(
                    "Creating SQLite connection: %s",
                    db_path,
                )

                cls._connection = sqlite3.connect(
                    database=str(db_path),
                    check_same_thread=False,
                )

            return cls._connection

        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================
    # Checkpointer
    # ==============================================================

    @classmethod
    def get_checkpointer(cls) -> SqliteSaver:
        """
        Return LangGraph SqliteSaver.
        """

        try:

            if cls._checkpointer is None:

                logging.info(
                    "Initializing LangGraph Checkpointer..."
                )

                cls._checkpointer = SqliteSaver(
                    conn=cls.get_connection()
                )

                logging.info(
                    "Checkpointer initialized successfully."
                )

            return cls._checkpointer

        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================
    # Close
    # ==============================================================

    @classmethod
    def close(cls) -> None:
        """
        Close SQLite connection.
        """

        try:

            if cls._connection:

                cls._connection.close()

                cls._connection = None
                cls._checkpointer = None

                logging.info(
                    "Checkpoint connection closed."
                )

        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================
    # Thread History
    # ==============================================================

    @classmethod
    def list_threads(cls) -> list[str]:
        """
        Return all stored thread IDs.
        """

        try:

            checkpointer = cls.get_checkpointer()

            thread_ids = set()

            for checkpoint in checkpointer.list(None):

                thread_ids.add(
                    checkpoint.config["configurable"]["thread_id"]
                )

            return sorted(thread_ids)

        except Exception as e:
            raise ChatBotException(e)

    # ==============================================================
    # Information
    # ==============================================================

    @classmethod
    def info(cls) -> dict:
        """
        Return checkpoint configuration.
        """

        return {
            "database": settings.CHECKPOINT_DB_PATH,
            "backend": "SQLite",
        }
    # ==============================================================
    # Connection Alias
    # ==============================================================

    @classmethod
    def connection(cls) -> sqlite3.Connection:
        """
        Alias for get_connection().
        """

        return cls.get_connection()


    # ==============================================================
    # Thread Exists
    # ==============================================================

    @classmethod
    def thread_exists(
        cls,
        thread_id: str,
    ) -> bool:
        """
        Check whether checkpoints exist for a thread.
        """

        try:

            return thread_id in cls.list_threads()

        except Exception as e:

            raise ChatBotException(e)


    # ==============================================================
    # Delete Thread Checkpoints
    # ==============================================================

    @classmethod
    def clear_thread(
        cls,
        thread_id: str,
    ) -> None:
        """
        Delete checkpoints for a specific thread.

        NOTE:
        LangGraph currently doesn't expose an official API
        to delete checkpoints individually.
        This method is left as a placeholder for future versions.
        """

        logging.warning(
            "Checkpoint deletion is not supported by "
            "LangGraph SQLite yet. Thread=%s",
            thread_id,
        )


    # ==============================================================
    # Clear All Checkpoints
    # ==============================================================

    @classmethod
    def clear_all(cls) -> None:
        """
        Remove every checkpoint from SQLite.
        """

        try:

            conn = cls.get_connection()

            cursor = conn.cursor()

            tables = [

                "checkpoints",

                "checkpoint_blobs",

                "checkpoint_writes",

            ]

            for table in tables:

                try:

                    cursor.execute(
                        f"DELETE FROM {table}"
                    )

                except Exception:

                    pass

            conn.commit()

            logging.info(
                "All checkpoints removed."
            )

        except Exception as e:

            raise ChatBotException(e)


    # ==============================================================
    # Health Check
    # ==============================================================

    @classmethod
    def ping(cls) -> bool:
        """
        Verify SQLite connection.
        """

        try:

            cls.get_connection().execute(
                "SELECT 1"
            )

            return True

        except Exception:

            return False