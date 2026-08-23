# services/vectorstore_service.py
"""
Production-ready Vector Store Service.

Features
--------
- FAISS support
- Chroma support
- Thread-specific vector stores
- Save / Load
- Delete
- Exists
- Retriever creation

This module attempts to import FAISS/Chroma from common locations and
fails late with an actionable error message if a store is requested but
the corresponding package is not installed.
"""

from __future__ import annotations

import importlib
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from config.config import settings
from core.exception import ChatBotException
from core.logger import logger
from services.embedding_service import EmbeddingService


def _locate_vector_classes() -> Tuple[Optional[type], Optional[type]]:
    """
    Attempt to locate FAISS and Chroma vectorstore classes from a few
    possible packages/locations. Returns (FAISS_class_or_None, Chroma_class_or_None).
    """
    FAISS_cls = None
    Chroma_cls = None

    # Candidate modules in decreasing priority
    candidates = [
        "langchain_community.vectorstores",
        "langchain_core.vectorstores",
        "langchain.vectorstores",
        "langchain_community",  # sometimes exposes under different path
    ]

    for mod_name in candidates:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        # try common class names
        if FAISS_cls is None:
            FAISS_cls = getattr(mod, "FAISS", None)
        if Chroma_cls is None:
            Chroma_cls = getattr(mod, "Chroma", None)
        # some community packages expose nested modules
        if FAISS_cls is None:
            FAISS_cls = getattr(mod, "faiss", None)
            if FAISS_cls and hasattr(FAISS_cls, "FAISS"):
                FAISS_cls = getattr(FAISS_cls, "FAISS", FAISS_cls)
        if Chroma_cls is None:
            Chroma_cls = getattr(mod, "chroma", None)
            if Chroma_cls and hasattr(Chroma_cls, "Chroma"):
                Chroma_cls = getattr(Chroma_cls, "Chroma", Chroma_cls)

    # Last attempt: try importing chromadb-backed class directly
    if Chroma_cls is None:
        try:
            mod = importlib.import_module("langchain.vectorstores")
            Chroma_cls = getattr(mod, "Chroma", None)
        except Exception:
            pass

    return FAISS_cls, Chroma_cls


FAISS_CLASS, CHROMA_CLASS = _locate_vector_classes()


class VectorStoreService:
    """
    Production Vector Store Manager.

    Use `vector_db` string to select backend: "faiss" or "chroma".
    """

    def __init__(
        self,
        vector_db: Optional[str] = None,
        thread_id: str = "default",
    ) -> None:
        # Use configured value or default
        self.vector_db = (vector_db or settings.VECTOR_DB).lower()
        self.thread_id = thread_id

        # Embedding model instance (LangChain Embeddings wrapper)
        self.embedding_model = EmbeddingService.get_embeddings()

        # persist directory for this thread
        # settings.VECTOR_STORE_DIR or similar must exist in config.settings
        persist_base = getattr(settings, "VECTOR_STORE_DIR", "data/vectorstore")
        self.persist_directory = Path(persist_base) / self.thread_id
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        logger.info("VectorStoreService initialized (backend=%s, thread=%s)", self.vector_db, self.thread_id)

    # ============================================================
    # Create
    # ============================================================
    def create(self, documents: List[Document]) -> VectorStore:
        """
        Create and return a vectorstore populated with the provided documents.
        """
        try:
            if not documents:
                raise ValueError("No documents found.")

            logger.info("Creating Vector Store (%s)...", self.vector_db)

            if self.vector_db == "faiss":
                if FAISS_CLASS is None:
                    raise RuntimeError(
                        "FAISS vectorstore class not available. "
                        "Install faiss and langchain-community: e.g. `pip install faiss-cpu langchain-community`."
                    )
                # Typical API: FAISS.from_documents(documents, embedding)
                vectorstore = FAISS_CLASS.from_documents(documents=documents, embedding=self.embedding_model)

            elif self.vector_db == "chroma":
                if CHROMA_CLASS is None:
                    raise RuntimeError(
                        "Chroma vectorstore class not available. "
                        "Install chromadb and a LangChain adapter: e.g. `pip install chromadb langchain-community`."
                    )
                vectorstore = CHROMA_CLASS.from_documents(
                    documents=documents,
                    embedding=self.embedding_model,
                    persist_directory=str(self.persist_directory),
                )
            else:
                raise ValueError(f"Unsupported Vector Store: {self.vector_db}")

            logger.info("Vector Store created successfully.")
            return vectorstore

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Save
    # ============================================================
    def save(self, vectorstore: VectorStore) -> None:
        try:
            logger.info("Saving Vector Store...")
            if self.vector_db == "faiss":
                # FAISS typically supports save_local
                if not hasattr(vectorstore, "save_local"):
                    raise RuntimeError("Provided FAISS vectorstore does not support save_local.")
                vectorstore.save_local(str(self.persist_directory))
            elif self.vector_db == "chroma":
                # Chroma typically uses persist()
                if not hasattr(vectorstore, "persist"):
                    raise RuntimeError("Provided Chroma vectorstore does not support persist().")
                vectorstore.persist()
            logger.info("Vector Store saved.")
        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Load
    # ============================================================
    def load(self) -> VectorStore:
        try:
            if self.vector_db == "faiss":
                if FAISS_CLASS is None:
                    raise RuntimeError(
                        "FAISS vectorstore class not available. "
                        "Install faiss-cpu and langchain-community: `pip install faiss-cpu langchain-community`."
                    )
                return FAISS_CLASS.load_local(
                    folder_path=str(self.persist_directory),
                    embeddings=self.embedding_model,
                    allow_dangerous_deserialization=True,
                )
            elif self.vector_db == "chroma":
                if CHROMA_CLASS is None:
                    raise RuntimeError(
                        "Chroma vectorstore class not available. "
                        "Install chromadb and langchain-community: `pip install chromadb langchain-community`."
                    )
                # Construct Chroma object
                return CHROMA_CLASS(persist_directory=str(self.persist_directory), embedding_function=self.embedding_model)
            else:
                raise ValueError("Unsupported Vector Store.")
        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Delete / Exists
    # ============================================================
    def exists(self) -> bool:
        return self.persist_directory.exists() and any(self.persist_directory.iterdir())

    def delete(self) -> None:
        try:
            if self.persist_directory.exists():
                shutil.rmtree(self.persist_directory)
                logger.info("Deleted vector store at %s", self.persist_directory)
        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Retriever creation
    # ============================================================
    def create_vectorstore(self, documents: List[Document]) -> VectorStore:
        """
        Backwards-compatible alias used in older code (create_vectorstore).
        """
        return self.create(documents)