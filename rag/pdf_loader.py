"""
rag/pdf_loader.py

Production-ready PDF document loader.

Responsibilities
----------------
- Validate PDF file
- Load PDF documents
- Attach metadata
- Return LangChain Documents
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from core.exception import ChatBotException
from core.logger import logging

from rag.base_loader import BaseLoader


class PDFLoader(BaseLoader):
    """
    PDF document loader.
    """

    @property
    def loader_name(self) -> str:
        return "PDF Loader"

    @property
    def supported_extensions(self) -> List[str]:
        return [".pdf"]

    def load(
        self,
        source: str | Path,
    ) -> List[Document]:
        """
        Load a PDF file.

        Parameters
        ----------
        source : str | Path

        Returns
        -------
        List[Document]
        """

        try:

            source = Path(source)

            if not source.exists():

                raise FileNotFoundError(
                    f"File not found: {source}"
                )

            logging.info(
                "Loading PDF: %s",
                source.name,
            )

            loader = PyPDFLoader(str(source))

            documents = loader.load()

            # -----------------------------------------------------
            # Add custom metadata
            # -----------------------------------------------------

            for document in documents:

                document.metadata.update(
                    {
                        "document_type": "pdf",
                        "file_name": source.name,
                        "file_path": str(source),
                    }
                )

            logging.info(
                "Loaded %d pages from %s",
                len(documents),
                source.name,
            )

            return documents

        except Exception as e:

            raise ChatBotException(e)