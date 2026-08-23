# rag/loader_factory.py
"""
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
from typing import Iterable, Type

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

    Note: store loader *classes* here and instantiate on demand to avoid
    side-effects (e.g., loaders reading settings) at import-time.
    """

    # Keep classes (not instances) to avoid import-time instantiation
    _loader_classes: list[Type[BaseLoader]] = [
        PDFLoader,
        DocxLoader,
        TXTLoader,
        YouTubeLoader,
    ]

    # ---------------------------------------------------------
    @classmethod
    def _instantiate_loader(cls, loader_cls_or_instance) -> BaseLoader:
        """
        Return an instance for a loader class or return the instance unchanged.
        """
        if isinstance(loader_cls_or_instance, type):
            return loader_cls_or_instance()
        return loader_cls_or_instance

    # ---------------------------------------------------------
    @classmethod
    def get_loader(cls, source: str) -> BaseLoader:
        """
        Return appropriate loader based on source.
        """
        try:
            source = str(source).strip()

            # -----------------------------------------
            # YouTube URL (handle early and return instance)
            # -----------------------------------------
            if source.startswith("http://") or source.startswith("https://"):
                if "youtube.com" in source or "youtu.be" in source:
                    logging.info("Selected YouTube Loader")
                    return YouTubeLoader()

            # -----------------------------------------
            # Local Files - check suffix against loader.supported_extensions
            # -----------------------------------------
            suffix = Path(source).suffix.lower()

            for loader_cls in cls._loader_classes:
                # instantiate on demand
                loader = cls._instantiate_loader(loader_cls)
                if suffix in loader.supported_extensions:
                    logging.info("Selected %s", loader.loader_name)
                    return loader

            raise ValueError(f"Unsupported document type: {suffix}")

        except Exception as e:
            raise ChatBotException(e)

    # ---------------------------------------------------------
    @classmethod
    def supported_formats(cls) -> list[str]:
        """
        Return supported formats. Avoid instantiating loaders that might have
        side-effects; treat YouTube specially (string 'youtube').
        """
        formats = set()

        for loader_cls in cls._loader_classes:
            # Avoid instantiating YouTubeLoader only for supported_formats,
            # and just include the 'youtube' token directly.
            if loader_cls is YouTubeLoader:
                formats.add("youtube")
                continue
            # instantiate other loaders to query supported_extensions
            try:
                loader = loader_cls()
                formats.update(loader.supported_extensions)
            except Exception:
                # If instantiation fails for some loader, skip it
                logging.debug("Could not instantiate loader %s when computing supported formats.", loader_cls)
                continue

        return sorted(formats)

    # ---------------------------------------------------------
    @classmethod
    def is_supported(cls, source: str) -> bool:
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
    def register_loader(cls, loader: type[BaseLoader] | BaseLoader) -> None:
        """
        Register a custom loader. Accept loader class or instance.
        """
        if isinstance(loader, type):
            cls._loader_classes.append(loader)
        else:
            # store class for consistency
            cls._loader_classes.append(loader.__class__)

        logging.info("Registered Loader : %s", getattr(loader, "loader_name", str(loader)))