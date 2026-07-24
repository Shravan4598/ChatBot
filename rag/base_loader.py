"""
rag/base_loader.py

Abstract Base Loader for all document loaders.

Every document loader (PDF, DOCX, TXT, YouTube)
must inherit from this class.

Benefits
--------
- Consistent interface
- Easy to extend
- Better dependency injection
- Supports future loaders
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from langchain_core.documents import Document


class BaseLoader(ABC):
    """
    Abstract base class for all document loaders.
    """

    @abstractmethod
    def load(
        self,
        source: str | Path,
    ) -> List[Document]:
        """
        Load documents from the given source.

        Parameters
        ----------
        source : str | Path
            Source path or URL.

        Returns
        -------
        List[Document]
            Loaded LangChain documents.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def loader_name(self) -> str:
        """
        Return loader name.

        Returns
        -------
        str
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        Supported file extensions.

        Example
        -------
        PDF Loader:
            [".pdf"]

        DOCX Loader:
            [".docx"]

        TXT Loader:
            [".txt"]

        YouTube Loader:
            ["youtube"]
        """
        raise NotImplementedError