"""
rag/docx_loader.py

Production-ready DOCX document loader.

Responsibilities
----------------
- Validate DOCX file
- Load Microsoft Word documents
- Attach metadata
- Return LangChain Documents
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader

from core.exception import ChatBotException
from core.logger import logging

from rag.base_loader import BaseLoader


class DocxLoader(BaseLoader):
    """
    Microsoft Word (.docx) loader.
    """

    @property
    def loader_name(self) -> str:
        return "DOCX Loader"

    @property
    def supported_extensions(self) -> List[str]:
        return [".docx"]

    def load(
        self,
        source: str | Path,
    ) -> List[Document]:
        """
        Load a DOCX file.

        Parameters
        ----------
        source : str | Path
            Path to the DOCX file.

        Returns
        -------
        List[Document]
            Loaded LangChain documents.
        """

        try:

            source = Path(source)

            if not source.exists():
                raise FileNotFoundError(
                    f"File not found: {source}"
                )

            logging.info(
                "Loading DOCX document: %s",
                source.name,
            )

            loader = Docx2txtLoader(str(source))

            documents = loader.load()

            # --------------------------------------------------
            # Add metadata
            # --------------------------------------------------

            for document in documents:

                document.metadata.update(
                    {
                        "document_type": "docx",
                        "file_name": source.name,
                        "file_path": str(source),
                    }
                )

            logging.info(
                "Loaded %d document(s) from %s",
                len(documents),
                source.name,
            )

            return documents

        except Exception as e:

            raise ChatBotException(e)