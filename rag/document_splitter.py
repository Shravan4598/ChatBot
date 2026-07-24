"""
rag/document_splitter.py

Production-ready document splitter.

Responsibilities
----------------
- Split LangChain Documents into chunks
- Preserve metadata
- Configurable chunk size and overlap
- Support all document types
"""

from __future__ import annotations

from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging


class DocumentSplitter:
    """
    Production document splitter.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        """
        Initialize document splitter.
        """

        self.chunk_size = (
            chunk_size
            or settings.CHUNK_SIZE
        )

        self.chunk_overlap = (
            chunk_overlap
            or settings.CHUNK_OVERLAP
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "? ",
                "! ",
                ";",
                ",",
                " ",
                "",
            ],
            length_function=len,
            is_separator_regex=False,
        )

        logging.info(
            "DocumentSplitter initialized "
            "(chunk_size=%d, overlap=%d)",
            self.chunk_size,
            self.chunk_overlap,
        )

    # ==========================================================
    # Split Documents
    # ==========================================================

    def split_documents(
        self,
        documents: List[Document],
    ) -> List[Document]:
        """
        Split LangChain documents.

        Returns
        -------
        List[Document]
        """

        try:

            if not documents:
                raise ValueError(
                    "No documents supplied."
                )

            logging.info(
                "Splitting %d document(s)...",
                len(documents),
            )

            chunks = self.splitter.split_documents(
                documents
            )

            # --------------------------------------------
            # Add chunk metadata
            # --------------------------------------------

            for index, chunk in enumerate(chunks):

                chunk.metadata.update(
                    {
                        "chunk_id": index + 1,
                        "chunk_size": len(
                            chunk.page_content
                        ),
                    }
                )

            logging.info(
                "Generated %d chunks.",
                len(chunks),
            )

            return chunks

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Split Text
    # ==========================================================

    def split_text(
        self,
        text: str,
    ) -> List[str]:
        """
        Split raw text.
        """

        try:

            if not text.strip():
                return []

            chunks = self.splitter.split_text(
                text
            )

            logging.info(
                "Generated %d text chunks.",
                len(chunks),
            )

            return chunks

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Configuration
    # ==========================================================

    @property
    def configuration(self) -> dict:
        """
        Return splitter configuration.
        """

        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }