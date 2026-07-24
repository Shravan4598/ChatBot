"""
services/conversation_service.py

Production Conversation Service.

Responsibilities
----------------
• Manage conversation metadata
• Create conversations
• Rename conversations
• Delete conversations
• List conversations
• Search conversations
• Update last message
• Store timestamps

NOTE:
Uses the same SQLite database as LangGraph checkpoints.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime
from typing import Optional
from services.checkpoint_service import CheckpointService

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging



class ConversationService:
    """
    Manage conversation metadata.
    """

    TABLE_NAME = "conversations"

    def __init__(self) -> None:

        try:

            self.connection = CheckpointService.get_connection()

            self.connection.row_factory = sqlite3.Row

            self.cursor = self.connection.cursor()

            self._create_table()

            logging.info(
                "ConversationService initialized."
            )

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Table
    # ==========================================================

    def _create_table(self) -> None:

        query = f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME}
        (

            thread_id TEXT PRIMARY KEY,

            title TEXT NOT NULL,

            last_message TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL

        );
        """

        self.cursor.execute(query)

        self.connection.commit()

    # ==========================================================
    # Create Conversation
    # ==========================================================

    def create(
        self,
        title: str = "New Chat",
    ) -> str:

        try:

            thread_id = str(uuid.uuid4())

            now = datetime.utcnow().isoformat()

            self.cursor.execute(

                f"""
                INSERT INTO {self.TABLE_NAME}
                (

                    thread_id,

                    title,

                    last_message,

                    created_at,

                    updated_at

                )

                VALUES
                (?, ?, ?, ?, ?)
                """,

                (

                    thread_id,

                    title,

                    "",

                    now,

                    now,

                ),

            )

            self.connection.commit()

            logging.info(
                "Conversation created."
            )

            return thread_id

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Update
    # ==========================================================

    def update_message(
        self,
        thread_id: str,
        message: str,
    ) -> None:

        try:

            self.cursor.execute(

                f"""
                UPDATE {self.TABLE_NAME}

                SET

                    last_message=?,

                    updated_at=?

                WHERE thread_id=?
                """,

                (

                    message,

                    datetime.utcnow().isoformat(),

                    thread_id,

                ),

            )

            self.connection.commit()

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Rename
    # ==========================================================

    def rename(
        self,
        thread_id: str,
        title: str,
    ) -> None:

        try:

            self.cursor.execute(

                f"""
                UPDATE {self.TABLE_NAME}

                SET

                    title=?,

                    updated_at=?

                WHERE thread_id=?
                """,

                (

                    title,

                    datetime.utcnow().isoformat(),

                    thread_id,

                ),

            )

            self.connection.commit()

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Delete
    # ==========================================================

    def delete(
        self,
        thread_id: str,
    ) -> None:

        try:

            self.cursor.execute(

                f"""
                DELETE FROM {self.TABLE_NAME}

                WHERE thread_id=?
                """,

                (thread_id,),

            )

            self.connection.commit()

            logging.info(
                "Conversation deleted."
            )

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Exists
    # ==========================================================

    def exists(
        self,
        thread_id: str,
    ) -> bool:

        self.cursor.execute(

            f"""
            SELECT thread_id

            FROM {self.TABLE_NAME}

            WHERE thread_id=?
            """,

            (thread_id,),

        )

        return self.cursor.fetchone() is not None

    # ==========================================================
    # Get
    # ==========================================================

    def get(
        self,
        thread_id: str,
    ) -> Optional[dict]:

        self.cursor.execute(

            f"""
            SELECT *

            FROM {self.TABLE_NAME}

            WHERE thread_id=?
            """,

            (thread_id,),

        )

        row = self.cursor.fetchone()

        if row is None:

            return None

        return dict(row)

    # ==========================================================
    # List
    # ==========================================================

    def list_conversations(
        self,
    ) -> list[dict]:

        self.cursor.execute(

            f"""
            SELECT *

            FROM {self.TABLE_NAME}

            ORDER BY updated_at DESC
            """

        )

        rows = self.cursor.fetchall()

        return [

            dict(row)

            for row in rows

        ]

    # ==========================================================
    # Search
    # ==========================================================

    def search(
        self,
        keyword: str,
    ) -> list[dict]:

        self.cursor.execute(

            f"""
            SELECT *

            FROM {self.TABLE_NAME}

            WHERE

                title LIKE ?

                OR

                last_message LIKE ?

            ORDER BY updated_at DESC
            """,

            (

                f"%{keyword}%",

                f"%{keyword}%",

            ),

        )

        rows = self.cursor.fetchall()

        return [

            dict(row)

            for row in rows

        ]

    # ==========================================================
    # Count
    # ==========================================================

    def count(self) -> int:

        self.cursor.execute(

            f"""
            SELECT COUNT(*)

            FROM {self.TABLE_NAME}
            """

        )

        return self.cursor.fetchone()[0]

    # ==========================================================
    # Close
    # ==========================================================

    def close(self) -> None:

        self.connection.close()