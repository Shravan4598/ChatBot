"""
services/vectorstore_service.py

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
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma

from config.config import settings
from config.constants import FAISS, CHROMA
from core.exception import ChatBotException
from core.logger import logging
from services.embedding_service import EmbeddingService


class VectorStoreService:
    """
    Production Vector Store Manager.
    """

    def __init__(
        self,
        vector_db: Optional[str] = None,
        thread_id: str = "default",
    ) -> None:

        self.vector_db = (
            vector_db or settings.VECTOR_STORE_TYPE
        ).lower()

        self.thread_id = thread_id

        self.embedding_model = (
            EmbeddingService.get_embeddings()
        )

        self.persist_directory = (
            Path(settings.VECTOR_STORE_PATH)
            / self.thread_id
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ============================================================
    # Create
    # ============================================================

    def create(
        self,
        documents: List[Document],
    ) -> VectorStore:

        try:

            if not documents:
                raise ValueError(
                    "No documents found."
                )

            logging.info(
                "Creating Vector Store (%s)...",
                self.vector_db,
            )

            if self.vector_db == FAISS:

                vectorstore = FAISS.from_documents(
                    documents=documents,
                    embedding=self.embedding_model,
                )

            elif self.vector_db == CHROMA:

                vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embedding_model,
                    persist_directory=str(
                        self.persist_directory
                    ),
                )

            else:

                raise ValueError(
                    f"Unsupported Vector Store: {self.vector_db}"
                )

            logging.info(
                "Vector Store created successfully."
            )

            return vectorstore

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Save
    # ============================================================

    def save(
        self,
        vectorstore: VectorStore,
    ) -> None:

        try:

            logging.info(
                "Saving Vector Store..."
            )

            if self.vector_db == FAISS:

                vectorstore.save_local(
                    str(self.persist_directory)
                )

            elif self.vector_db == CHROMA:

                vectorstore.persist()

            logging.info(
                "Vector Store saved."
            )

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Load
    # ============================================================

    def load(self) -> VectorStore:

        try:

            if self.vector_db == FAISS:

                return FAISS.load_local(
                    folder_path=str(
                        self.persist_directory
                    ),
                    embeddings=self.embedding_model,
                    allow_dangerous_deserialization=True,
                )

            elif self.vector_db == CHROMA:

                return Chroma(
                    persist_directory=str(
                        self.persist_directory
                    ),
                    embedding_function=self.embedding_model,
                )

            raise ValueError(
                "Unsupported Vector Store."
            )

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Exists
    # ============================================================

    def exists(self) -> bool:

        if not self.persist_directory.exists():
            return False

        if self.vector_db == FAISS:

            return (
                (self.persist_directory / "index.faiss").exists()
                and
                (self.persist_directory / "index.pkl").exists()
            )

        elif self.vector_db == CHROMA:

            return any(
                self.persist_directory.iterdir()
            )

        return False

    # ============================================================
    # Delete
    # ============================================================

    def delete(self) -> None:

        try:

            if self.persist_directory.exists():

                shutil.rmtree(
                    self.persist_directory
                )

                logging.info(
                    "Vector Store deleted."
                )

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Retriever
    # ============================================================

    def get_retriever(
        self,
        vectorstore: VectorStore,
        search_type: str = "similarity",
        k: Optional[int] = None,
    ):

        try:

            retriever = vectorstore.as_retriever(
                search_type=search_type,
                search_kwargs={
                    "k": k or settings.RETRIEVER_TOP_K
                },
            )

            logging.info(
                "Retriever created."
            )

            return retriever

        except Exception as e:
            raise ChatBotException(e)

    # ============================================================
    # Configuration
    # ============================================================

    @property
    def configuration(self) -> dict:

        return {
            "vector_store": self.vector_db,
            "thread_id": self.thread_id,
            "persist_directory": str(
                self.persist_directory
            ),
        }