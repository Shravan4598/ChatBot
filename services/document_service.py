"""
services/document_service.py

Centralized document management service.

Responsibilities
----------------
- Validate uploaded files
- Save uploaded documents
- Generate unique filenames
- Return document metadata
- Delete uploaded files
- List uploaded files
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from config.config import settings
from config.constants import SUPPORTED_DOCUMENTS
from core.exception import ChatBotException
from core.logger import logging


class DocumentService:
    """
    Service for managing uploaded documents.
    """

    def __init__(self, thread_id: str = "default") -> None:

        self.thread_id = thread_id

        self.upload_directory = (
            Path(settings.UPLOAD_DIRECTORY)
            / thread_id
        )

        self.upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ============================================================
    # Validate
    # ============================================================

    @staticmethod
    def validate_file(filename: str) -> None:
        """
        Validate file extension.
        """

        suffix = Path(filename).suffix.lower()

        if suffix not in SUPPORTED_DOCUMENTS:

            raise ChatBotException(
                ValueError(
                    f"Unsupported file type: {suffix}"
                )
            )

    # ============================================================
    # Save
    # ============================================================

    def save_file(
        self,
        uploaded_file: BinaryIO,
    ) -> dict:
        """
        Save uploaded file.

        Returns
        -------
        dict
            File metadata.
        """

        try:

            self.validate_file(uploaded_file.name)

            extension = Path(
                uploaded_file.name
            ).suffix.lower()

            unique_name = (
                f"{uuid.uuid4().hex}{extension}"
            )

            destination = (
                self.upload_directory
                / unique_name
            )

            with open(destination, "wb") as file:

                shutil.copyfileobj(
                    uploaded_file,
                    file,
                )

            logging.info(
                "Document saved: %s",
                destination.name,
            )

            return {
                "thread_id": self.thread_id,
                "original_name": uploaded_file.name,
                "saved_name": unique_name,
                "path": str(destination),
                "extension": extension,
                "size": destination.stat().st_size,
            }

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Delete
    # ============================================================

    def delete_file(
        self,
        filename: str,
    ) -> None:

        try:

            file_path = (
                self.upload_directory
                / filename
            )

            if file_path.exists():

                file_path.unlink()

                logging.info(
                    "Deleted document: %s",
                    filename,
                )

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # List Files
    # ============================================================

    def list_files(self) -> list[dict]:
        """
        Return uploaded file information.
        """

        try:

            documents = []

            for file in sorted(
                self.upload_directory.glob("*")
            ):

                if file.is_file():

                    documents.append(
                        {
                            "name": file.name,
                            "path": str(file),
                            "size": file.stat().st_size,
                            "extension": file.suffix,
                        }
                    )

            return documents

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Clear Thread Files
    # ============================================================

    def clear(self) -> None:
        """
        Delete every uploaded file
        for this thread.
        """

        try:

            if self.upload_directory.exists():

                shutil.rmtree(
                    self.upload_directory
                )

                self.upload_directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                logging.info(
                    "Thread documents cleared."
                )

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Exists
    # ============================================================

    def exists(self) -> bool:
        """
        Check if thread contains uploaded files.
        """

        return any(
            self.upload_directory.glob("*")
        )