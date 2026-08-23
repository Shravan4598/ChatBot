# tools/rag_tool.py
"""
tools/rag_tool.py

Production RAG Tool.

Responsibilities
----------------
- Query uploaded documents
- Use RAG service
- Return grounded answers
"""

from __future__ import annotations

from core.exception import ChatBotException
from core.logger import logger

from tools.base_tool import BaseTool
from rag.rag_service import RAGService


class RAGTool(BaseTool):
    """
    Production RAG Tool.
    """

    def __init__(self) -> None:
        self.rag_service = RAGService()
        logger.info("RAG Tool initialized.")

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:
        return "rag_tool"

    @property
    def description(self) -> str:
        return (
            "Answer questions using uploaded "
            "documents only."
        )

    # ==========================================================
    # Ask Question
    # ==========================================================
    def invoke(self, question: str) -> str:
        """
        Ask a question over uploaded documents.
        """
        try:
            logger.info("Running RAG query.")
            response = self.rag_service.ask(question)
            logger.info("RAG response generated.")
            return response
        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Index Documents
    # ==========================================================
    def ingest(self, file_path: str) -> None:
        """
        Build vector database from a document.
        """
        try:
            logger.info("Indexing document : %s", file_path)
            # RAGService provides build(source) to create the pipeline from a source.
            self.rag_service.build(file_path)
            logger.info("Document indexed successfully.")
        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Status
    # ==========================================================
    @property
    def ready(self) -> bool:
        return self.rag_service.ready

    # ==========================================================
    # Reset
    # ==========================================================
    def reset(self) -> None:
        self.rag_service.reset()
        logger.info("RAG Tool reset.")