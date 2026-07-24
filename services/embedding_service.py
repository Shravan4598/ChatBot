"""
services/embedding_service.py

Centralized embedding model service.

Supports:
1. Google Generative AI Embeddings
2. HuggingFace Embeddings

The provider is selected from config.py.
"""

from __future__ import annotations

from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging


class EmbeddingService:
    """
    Singleton Embedding Service.
    """

    _instance: Optional[Embeddings] = None

    @classmethod
    def get_embeddings(cls) -> Embeddings:
        """
        Return embedding model instance.
        """

        try:

            if cls._instance is not None:
                return cls._instance

            provider = settings.EMBEDDING_PROVIDER.lower()

            logging.info(
                "Loading Embedding Provider: %s",
                provider,
            )

            # ---------------------------------------------------------
            # Google Embeddings
            # ---------------------------------------------------------

            if provider == "google":

                cls._instance = GoogleGenerativeAIEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                )

            # ---------------------------------------------------------
            # HuggingFace Embeddings
            # ---------------------------------------------------------

            elif provider == "huggingface":

                cls._instance = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL,
                    model_kwargs={
                        "device": settings.EMBEDDING_DEVICE
                    },
                    encode_kwargs={
                        "normalize_embeddings": True
                    },
                )

            else:

                raise ValueError(
                    f"Unsupported embedding provider: {provider}"
                )

            logging.info("Embedding model initialized successfully.")

            return cls._instance

        except Exception as e:
            raise ChatBotException(e)

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    @classmethod
    def reset(cls) -> None:
        """
        Reset singleton.
        """

        cls._instance = None

        logging.info(
            "Embedding singleton reset."
        )

    # ---------------------------------------------------------
    # Info
    # ---------------------------------------------------------

    @classmethod
    def model_name(cls) -> str:

        return settings.EMBEDDING_MODEL

    @classmethod
    def provider(cls) -> str:

        return settings.EMBEDDING_PROVIDER

    @classmethod
    def configuration(cls) -> dict:

        return {
            "provider": settings.EMBEDDING_PROVIDER,
            "model": settings.EMBEDDING_MODEL,
            "device": settings.EMBEDDING_DEVICE,
        }