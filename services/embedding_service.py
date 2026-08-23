# services/embedding_service.py
"""
Centralized embedding model service.

Supports multiple embedding providers while avoiding import-time failures
if optional provider packages are not installed.

Providers supported (attempted, in order):
- google (langchain_google_genai)
- huggingface (HuggingFace embeddings via langchain or langchain_huggingface)
- sentence-transformers via a LangChain wrapper (if present)

The implementation tries to import provider-specific classes only when required
and raises a clear error telling the user what to install if the requested
provider is unavailable.
"""

from __future__ import annotations

import importlib
from typing import Optional, Any

from langchain_core.embeddings import Embeddings  # LangChain core interface

from config.config import settings
from core.exception import ChatBotException
from core.logger import logger


class EmbeddingService:
    """
    Singleton Embedding Service.

    Use EmbeddingService.get_embeddings() to obtain an Embeddings-compatible instance.
    """

    _instance: Optional[Embeddings] = None

    @classmethod
    def _try_get_class(cls, module_names: list[str], class_name: str) -> Optional[type]:
        """
        Try to import a class by searching candidate modules.
        Returns the class or None if not found.
        """
        for mod_name in module_names:
            try:
                mod = importlib.import_module(mod_name)
            except Exception:
                continue
            cls_obj = getattr(mod, class_name, None)
            if cls_obj is not None:
                return cls_obj
        return None

    @classmethod
    def get_embeddings(cls) -> Embeddings:
        """
        Return embedding model instance. Instantiates lazily and caches the result.
        """
        try:
            if cls._instance is not None:
                return cls._instance

            provider = getattr(settings, "EMBEDDING_PROVIDER", "huggingface")
            provider = str(provider).strip().lower()

            logger.info("Loading Embedding Provider: %s", provider)

            # ---------------------------
            # Google Generative AI
            # ---------------------------
            if provider in ("google", "google_genai", "genai", "google-genai"):
                # Candidate module names that projects sometimes use
                candidates = [
                    "langchain_google_genai",
                    "langchain_genai",
                    "langchain.google_genai",
                ]
                cls_obj = cls._try_get_class(candidates, "GoogleGenerativeAIEmbeddings")
                if cls_obj is None:
                    raise RuntimeError(
                        "Google Generative AI embeddings provider requested but package not installed. "
                        "Install a compatible package, e.g. `pip install langchain-google-genai google-generative-ai`."
                    )
                # Instantiate with safe lookups for required settings
                google_api_key = getattr(settings, "GOOGLE_API_KEY", getattr(settings, "GEMINI_API_KEY", None))
                model = getattr(settings, "EMBEDDING_MODEL", None)
                cls._instance = cls_obj(model=model, google_api_key=google_api_key)
                logger.info("Google Generative AI embeddings initialized.")
                return cls._instance

            # ---------------------------
            # HuggingFace Embeddings (LangChain wrapper)
            # ---------------------------
            if provider in ("huggingface", "hf", "hugging-face"):
                # Try a few module paths
                candidates = [
                    "langchain_huggingface",
                    "langchain.embeddings",
                    "langchain_hub",
                ]
                cls_obj = cls._try_get_class(candidates, "HuggingFaceEmbeddings")
                if cls_obj is None:
                    # Another common import location is `langchain_huggingface` package
                    raise RuntimeError(
                        "HuggingFace embeddings requested but the LangChain HuggingFace wrapper is not available. "
                        "Install e.g. `pip install sentence-transformers langchain` and the appropriate langchain-huggingface adapter "
                        "for your LangChain version (e.g. `pip install langchain-huggingface`)."
                    )

                model_name = getattr(settings, "EMBEDDING_MODEL", None)
                device = getattr(settings, "EMBEDDING_DEVICE", None)
                # Construct kwargs safely
                constructor_kwargs: dict[str, Any] = {}
                if model_name:
                    # Different wrappers expect different kwarg names; try common variants
                    try:
                        cls._instance = cls_obj(model_name=model_name)
                    except TypeError:
                        # alternative constructor kwarg name
                        cls._instance = cls_obj(model=model_name)
                else:
                    # No explicit model, attempt default construction
                    cls._instance = cls_obj()

                # If class expects model_kwargs / encode_kwargs, attempt best-effort configuration
                try:
                    # Many wrappers accept model_kwargs param
                    if device and hasattr(cls._instance, "__dict__"):
                        # set attribute if exists (best-effort)
                        setattr(cls._instance, "model_kwargs", {"device": device})
                except Exception:
                    pass

                logger.info("HuggingFace embeddings initialized.")
                return cls._instance

            # ---------------------------
            # Sentence-Transformers via generic wrappers
            # ---------------------------
            if provider in ("sentence-transformers", "sbert", "s-t"):
                # Try to find a wrapper class typically named SentenceTransformerEmbeddings or similar
                candidates = [
                    "langchain.embeddings",
                    "langchain_huggingface",
                    "langchain_sentence_transformers",
                ]
                cls_obj = cls._try_get_class(candidates, "SentenceTransformerEmbeddings") or cls._try_get_class(
                    candidates, "SentenceTransformersEmbeddings"
                )
                if cls_obj is None:
                    raise RuntimeError(
                        "Sentence-Transformers provider requested but no wrapper found. "
                        "Install sentence-transformers and an appropriate LangChain wrapper: `pip install sentence-transformers langchain`."
                    )
                model_name = getattr(settings, "EMBEDDING_MODEL", None)
                if model_name:
                    cls._instance = cls_obj(model_name=model_name)
                else:
                    cls._instance = cls_obj()
                logger.info("Sentence-Transformers embeddings initialized.")
                return cls._instance

            # ---------------------------
            # Default fallback: try common HuggingFace wrapper automatically
            # ---------------------------
            # Try to find HuggingFaceEmbeddings automatically before failing
            fallback_candidates = ["langchain_huggingface", "langchain.embeddings"]
            cls_obj = cls._try_get_class(fallback_candidates, "HuggingFaceEmbeddings")
            if cls_obj:
                model_name = getattr(settings, "EMBEDDING_MODEL", None)
                if model_name:
                    cls._instance = cls_obj(model_name=model_name)
                else:
                    cls._instance = cls_obj()
                logger.info("Fallback HuggingFace embeddings initialized.")
                return cls._instance

            # If we reach here, no suitable provider could be used
            raise RuntimeError(
                "No supported embedding provider is available. Set settings.EMBEDDING_PROVIDER to 'huggingface' or 'google' "
                "and install the corresponding packages. Example: `pip install sentence-transformers langchain` for HuggingFace "
                "or `pip install langchain-google-genai google-generative-ai` for Google Generative Embeddings."
            )

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
        logger.info("Embedding singleton reset.")

    # ---------------------------------------------------------
    # Info getters
    # ---------------------------------------------------------
    @classmethod
    def model_name(cls) -> str:
        return getattr(settings, "EMBEDDING_MODEL", "unknown")

    @classmethod
    def provider(cls) -> str:
        return getattr(settings, "EMBEDDING_PROVIDER", "unknown")

    @classmethod
    def configuration(cls) -> dict:
        return {
            "provider": getattr(settings, "EMBEDDING_PROVIDER", None),
            "model": getattr(settings, "EMBEDDING_MODEL", None),
            "device": getattr(settings, "EMBEDDING_DEVICE", None),
        }