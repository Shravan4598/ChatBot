"""
rag/loader_factory.py

Factory for selecting the appropriate document loader.

Supported Sources
-----------------
- PDF
- DOCX
- TXT
- YouTube

New loaders can be registered without changing
the RAG pipeline.
"""

from __future__ import annotations

from pathlib import Path

from core.exception import ChatBotException
from core.logger import logging

from rag.base_loader import BaseLoader
from rag.docx_loader import DocxLoader
from rag.pdf_loader import PDFLoader
from rag.txt_loader import TXTLoader
from rag.youtube_loader import YouTubeLoader


class LoaderFactory:
    """
    Factory for creating document loaders.
    """

    _loaders = [
        PDFLoader(),
        DocxLoader(),
        TXTLoader(),
        YouTubeLoader(),
    ]

    # ---------------------------------------------------------

    @classmethod
    def get_loader(
        cls,
        source: str,
    ) -> BaseLoader:
        """
        Return appropriate loader based on source.
        """

        try:

            source = str(source).strip()

            # -----------------------------------------
            # YouTube URL
            # -----------------------------------------

            if (
                source.startswith("http://")
                or source.startswith("https://")
            ):

                if (
                    "youtube.com" in source
                    or "youtu.be" in source
                ):

                    logging.info(
                        "Selected YouTube Loader"
                    )

                    return YouTubeLoader()

            # -----------------------------------------
            # Local Files
            # -----------------------------------------

            suffix = Path(source).suffix.lower()

            for loader in cls._loaders:

                if (
                    suffix
                    in loader.supported_extensions
                ):

                    logging.info(
                        "Selected %s",
                        loader.loader_name,
                    )

                    return loader

            raise ValueError(
                f"Unsupported document type: {suffix}"
            )

        except Exception as e:

            raise ChatBotException(e)

    # ---------------------------------------------------------

    @classmethod
    def supported_formats(cls) -> list[str]:
        """
        Return supported formats.
        """

        formats = []

        for loader in cls._loaders:

            formats.extend(
                loader.supported_extensions
            )

        formats.append("youtube")

        return sorted(set(formats))

    # ---------------------------------------------------------

    @classmethod
    def is_supported(
        cls,
        source: str,
    ) -> bool:
        """
        Check whether a source is supported.
        """

        try:

            cls.get_loader(source)

            return True

        except Exception:

            return False

    # ---------------------------------------------------------

    @classmethod
    def register_loader(
        cls,
        loader: BaseLoader,
    ) -> None:
        """
        Register a custom loader.
        """

        cls._loaders.append(loader)

        logging.info(
            "Registered Loader : %s",
            loader.loader_name,
        )