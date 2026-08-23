"""
rag/rag_service.py

Production RAG Service.

Responsibilities
----------------
- Load documents
- Split documents
- Create embeddings
- Build vector store
- Create retriever
- Build RAG chain
- Answer questions
- Reset pipeline
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from langchain_core.messages import BaseMessage

from core.exception import ChatBotException
from core.logger import logging

from rag.loader_factory import LoaderFactory
from rag.document_splitter import DocumentSplitter
from rag.retriever_service import RetrieverService
from rag.rag_chain import RAGChain

from services.vectorstore_service import VectorStoreService


class RAGService:
    """
    Production RAG Service.
    """

    def __init__(self) -> None:

        self.splitter = DocumentSplitter()

        self.vector_service = VectorStoreService()

        self.retriever_service: RetrieverService | None = None

        self.chain: RAGChain | None = None

        self.is_initialized = False

        logging.info("RAG Service initialized.")

    # ==========================================================
    # Build
    # ==========================================================

    def build(
        self,
        source: str | Path,
    ) -> dict:
        """
        Build RAG pipeline.

        Parameters
        ----------
        source:
            PDF, DOCX, TXT or YouTube URL.
        """

        try:

            logging.info(
                "Building RAG pipeline..."
            )

            loader = LoaderFactory.get_loader(
                str(source)
            )

            documents = loader.load(source)

            chunks = self.splitter.split_documents(
                documents
            )

            vector_store = (
                self.vector_service.create_vectorstore(
                    chunks
                )
            )

            self.retriever_service = (
                RetrieverService(
                    vector_store=vector_store
                )
            )

            self.chain = RAGChain(
                self.retriever_service.get_retriever()
            )

            self.is_initialized = True

            logging.info(
                "RAG pipeline built successfully."
            )

            return {

                "status": "success",

                "loader": loader.loader_name,

                "documents": len(documents),

                "chunks": len(chunks),

            }

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Ask
    # ==========================================================

    def ask(
        self,
        question: str,
        history: Optional[list[BaseMessage]] = None,
    ) -> str:

        try:

            if not self.is_initialized:

                raise RuntimeError(
                    "No document has been indexed."
                )

            return self.chain.invoke(
                question=question,
                history=history,
            )

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Stream
    # ==========================================================

    def stream(
        self,
        question: str,
        history: Optional[list[BaseMessage]] = None,
    ):

        try:

            if not self.is_initialized:

                raise RuntimeError(
                    "No document has been indexed."
                )

            yield from self.chain.stream(
                question=question,
                history=history,
            )

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Retrieve Documents
    # ==========================================================

    def retrieve_documents(
        self,
        query: str,
    ):

        if self.retriever_service is None:

            return []

        return self.retriever_service.retrieve(
            query
        )

    # ==========================================================
    # Retrieve Context
    # ==========================================================

    def retrieve_context(
        self,
        query: str,
    ) -> str:

        if self.retriever_service is None:

            return ""

        return self.retriever_service.retrieve_context(
            query
        )

    # ==========================================================
    # Metadata
    # ==========================================================

    def retrieve_metadata(
        self,
        query: str,
    ):

        if self.retriever_service is None:

            return []

        return self.retriever_service.retrieve_metadata(
            query
        )

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(self) -> None:

        self.chain = None

        self.retriever_service = None

        self.is_initialized = False

        logging.info(
            "RAG Service reset."
        )

    # ==========================================================
    # Status
    # ==========================================================

    @property
    def ready(self) -> bool:

        return self.is_initialized