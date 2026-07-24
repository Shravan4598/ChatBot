"""
rag/retriever_service.py

Production Retriever Service.

Responsibilities
----------------
- Create LangChain retrievers
- Support multiple retrieval strategies
- Retrieve relevant documents
- Expose retrieval configuration
"""

from __future__ import annotations

from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging


class RetrieverService:
    """
    Production Retriever Service.
    """

    VALID_SEARCH_TYPES = {
        "similarity",
        "mmr",
        "similarity_score_threshold",
    }

    def __init__(
        self,
        vector_store: VectorStore,
        search_type: str = "similarity",
        top_k: Optional[int] = None,
        fetch_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> None:

        self.vector_store = vector_store

        self.search_type = (
            search_type
            if search_type in self.VALID_SEARCH_TYPES
            else "similarity"
        )

        self.top_k = top_k or settings.RETRIEVER_TOP_K

        self.fetch_k = (
            fetch_k
            or settings.RETRIEVER_FETCH_K
        )

        self.score_threshold = (
            score_threshold
            or settings.RETRIEVER_SCORE_THRESHOLD
        )

        self._retriever: BaseRetriever | None = None

        logging.info(
            "Retriever initialized (%s)",
            self.search_type,
        )

    # ==========================================================
    # Create Retriever
    # ==========================================================

    def get_retriever(self) -> BaseRetriever:

        try:

            if self._retriever is None:

                kwargs = {
                    "k": self.top_k,
                }

                if self.search_type == "mmr":

                    kwargs["fetch_k"] = self.fetch_k

                elif (
                    self.search_type
                    == "similarity_score_threshold"
                ):

                    kwargs[
                        "score_threshold"
                    ] = self.score_threshold

                self._retriever = (
                    self.vector_store.as_retriever(
                        search_type=self.search_type,
                        search_kwargs=kwargs,
                    )
                )

                logging.info(
                    "Retriever created successfully."
                )

            return self._retriever

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Retrieve
    # ==========================================================

    def retrieve(
        self,
        query: str,
    ) -> List[Document]:

        try:

            logging.info(
                "Retrieving documents..."
            )

            documents = (
                self.get_retriever().invoke(query)
            )

            logging.info(
                "%d document(s) retrieved.",
                len(documents),
            )

            return documents

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Retrieve Context
    # ==========================================================

    def retrieve_context(
        self,
        query: str,
    ) -> str:
        """
        Return retrieved documents as a single string.
        """

        documents = self.retrieve(query)

        return "\n\n".join(
            document.page_content
            for document in documents
        )

    # ==========================================================
    # Retrieve Metadata
    # ==========================================================

    def retrieve_metadata(
        self,
        query: str,
    ) -> list[dict]:
        """
        Return metadata of retrieved documents.
        """

        documents = self.retrieve(query)

        return [
            document.metadata
            for document in documents
        ]

    # ==========================================================
    # Update
    # ==========================================================

    def update_configuration(

        self,

        *,

        search_type: Optional[str] = None,

        top_k: Optional[int] = None,

        fetch_k: Optional[int] = None,

        score_threshold: Optional[float] = None,

    ) -> None:

        if (
            search_type
            and search_type
            in self.VALID_SEARCH_TYPES
        ):
            self.search_type = search_type

        if top_k is not None:
            self.top_k = top_k

        if fetch_k is not None:
            self.fetch_k = fetch_k

        if score_threshold is not None:
            self.score_threshold = score_threshold

        self._retriever = None

        logging.info(
            "Retriever configuration updated."
        )

    # ==========================================================
    # Configuration
    # ==========================================================

    @property
    def configuration(self) -> dict:

        return {
            "search_type": self.search_type,
            "top_k": self.top_k,
            "fetch_k": self.fetch_k,
            "score_threshold": self.score_threshold,
        }