"""
rag/txt_loader.py

Production-ready TXT document loader.

Responsibilities
----------------
- Validate TXT files
- Load plain text documents
- Handle UTF-8 encoding
- Attach metadata
- Return LangChain Documents
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

from core.exception import ChatBotException
from core.logger import logging

from rag.base_loader import BaseLoader


class TXTLoader(BaseLoader):
    """
    Plain text (.txt) loader.
    """

    @property
    def loader_name(self) -> str:
        return "TXT Loader"

    @property
    def supported_extensions(self) -> List[str]:
        return [".txt"]

    def load(
        self,
        source: str | Path,
    ) -> List[Document]:
        """
        Load a text file.

        Parameters
        ----------
        source : str | Path
            Path to the TXT file.

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
                "Loading TXT document: %s",
                source.name,
            )

            loader = TextLoader(
                file_path=str(source),
                encoding="utf-8",
            )

            documents = loader.load()

            # --------------------------------------------
            # Add metadata
            # --------------------------------------------

            for document in documents:

                document.metadata.update(
                    {
                        "document_type": "txt",
                        "file_name": source.name,
                        "file_path": str(source),
                    }
                )

            logging.info(
                "Loaded %d TXT document(s).",
                len(documents),
            )

            return documents

        except UnicodeDecodeError:

            try:

                logging.warning(
                    "UTF-8 failed. Trying latin-1..."
                )

                loader = TextLoader(
                    file_path=str(source),
                    encoding="latin-1",
                )

                documents = loader.load()

                for document in documents:

                    document.metadata.update(
                        {
                            "document_type": "txt",
                            "file_name": source.name,
                            "file_path": str(source),
                        }
                    )

                return documents

            except Exception as e:
                raise ChatBotException(e)

        except Exception as e:
            raise ChatBotException(e)