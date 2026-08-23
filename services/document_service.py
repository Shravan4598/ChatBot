# services/document_service.py
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
from typing import BinaryIO, Iterable, Tuple

from config.config import settings
import config.constants as constants  # import the constants module, not specific names
from core.exception import ChatBotException
from core.logger import logger as logging  # use the configured logger (alias to logging)

# Resolve supported document suffixes from constants module, with fallbacks
_SUPPORTED_DOCS_CANDIDATES = (
    getattr(constants, "SUPPORTED_DOCUMENTS", None),
    getattr(constants, "ALLOWED_UPLOAD_SUFFIXES", None),
    getattr(constants, "SUPPORTED_DOC_EXTENSIONS", None),
)

def _normalize_supported(s: Iterable[str] | None) -> Tuple[str, ...]:
    if s is None:
        return (".pdf", ".txt", ".docx", ".md", ".pptx")
    # Accept sets, tuples, lists; ensure leading dot and lowercased
    out = []
    for item in s:
        if not isinstance(item, str):
            continue
        v = item.strip().lower()
        if not v.startswith("."):
            v = f".{v}"
        out.append(v)
    return tuple(sorted(set(out)))

SUPPORTED_DOCUMENTS = None
for candidate in _SUPPORTED_DOCS_CANDIDATES:
    if candidate:
        SUPPORTED_DOCUMENTS = _normalize_supported(candidate)
        break

if SUPPORTED_DOCUMENTS is None:
    SUPPORTED_DOCUMENTS = _normalize_supported(None)

class DocumentService:
    """
    Service for managing uploaded documents.
    """

    def __init__(self, thread_id: str = "default") -> None:
        self.thread_id = thread_id

        # Use setting name expected by project; fall back to constants.DOCS_DIR if missing
        upload_dir = getattr(settings, "UPLOAD_DIRECTORY", None) or getattr(settings, "DOCS_DIR", None) or str(constants.DOCS_DIR)

        self.upload_directory = Path(upload_dir) / thread_id

        self.upload_directory.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # Validate
    # ============================================================
    @staticmethod
    def validate_file(filename: str) -> None:
        """
        Validate file extension.
        Raises ChatBotException on invalid type.
        """
        suffix = Path(filename).suffix.lower()

        if suffix not in SUPPORTED_DOCUMENTS:
            raise ChatBotException(ValueError(f"Unsupported file type: {suffix}"))

    # ============================================================
    # Save
    # ============================================================
    def save_file(self, uploaded_file: BinaryIO) -> dict:
        """
        Save uploaded file.

        Returns
        -------
        dict
            File metadata.
        """
        try:
            # uploaded_file may be a file-like object with attribute 'name' (e.g., from Streamlit)
            name = getattr(uploaded_file, "name", None)
            if not name:
                raise ValueError("Uploaded file has no name attribute.")

            self.validate_file(name)

            extension = Path(name).suffix.lower()

            unique_name = f"{uuid.uuid4().hex}{extension}"

            destination = self.upload_directory / unique_name

            # Ensure uploaded_file is at start (if possible)
            try:
                uploaded_file.seek(0)
            except Exception:
                pass

            with open(destination, "wb") as file:
                shutil.copyfileobj(uploaded_file, file)

            logging.info("Document saved: %s", destination.name)

            return {
                "thread_id": self.thread_id,
                "original_name": name,
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
    def delete_file(self, filename: str) -> None:
        try:
            file_path = self.upload_directory / filename

            if file_path.exists():
                file_path.unlink()
                logging.info("Deleted document: %s", filename)

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
            for file in sorted(self.upload_directory.glob("*")):
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
        Delete every uploaded file for this thread.
        """
        try:
            if self.upload_directory.exists():
                shutil.rmtree(self.upload_directory)
                self.upload_directory.mkdir(parents=True, exist_ok=True)
                logging.info("Thread documents cleared.")
        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Exists
    # ============================================================
    def exists(self) -> bool:
        """
        Check if thread contains uploaded files.
        """
        return any(self.upload_directory.glob("*"))