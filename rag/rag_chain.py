"""
rag/rag_chain.py

Production RAG Chain.

Responsibilities
----------------
- Retrieve relevant context
- Build prompt
- Call Gemini
- Return grounded answer
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnablePassthrough,
)

from core.exception import ChatBotException
from core.logger import logging
from services.llm_service import LLMService


class RAGChain:
    """
    Production LCEL RAG Chain.
    """

    def __init__(self, retriever) -> None:

        self.retriever = retriever

        self.llm = LLMService.get_llm()

        self.parser = StrOutputParser()

        self.chain: Runnable | None = None

    # ==========================================================
    # Prompt
    # ==========================================================

    @staticmethod
    def _prompt() -> ChatPromptTemplate:

        return ChatPromptTemplate.from_messages(

            [

                (
                    "system",

                    """
You are an intelligent AI assistant.

Use ONLY the provided context.

If the answer is not present in the context,
reply with:

"I couldn't find this information in the uploaded documents."

Never hallucinate.

Always explain clearly.

If multiple sources support the answer,
combine them naturally.

Context

{context}

""",
                ),

                (
                    "placeholder",
                    "{history}",
                ),

                (
                    "human",
                    "{question}",
                ),

            ]

        )

    # ==========================================================
    # Context Formatter
    # ==========================================================

    @staticmethod
    def _format_documents(
        documents: List[Document],
    ) -> str:

        if not documents:

            return "No relevant context found."

        context = []

        for document in documents:

            source = document.metadata.get(
                "file_name",
                document.metadata.get(
                    "source",
                    "Unknown",
                ),
            )

            page = document.metadata.get(
                "page",
                None,
            )

            if page is not None:

                header = (
                    f"[Source: {source} | Page {page}]"
                )

            else:

                header = (
                    f"[Source: {source}]"
                )

            context.append(

                f"{header}\n\n{document.page_content}"

            )

        return "\n\n-------------------\n\n".join(
            context
        )

    # ==========================================================
    # Build
    # ==========================================================

    def build(self) -> Runnable:

        try:

            if self.chain is None:

                prompt = self._prompt()

                self.chain = (

                    {

                        "context":

                            self.retriever
                            | RunnableLambda(
                                self._format_documents
                            ),

                        "question":
                            RunnablePassthrough(),

                        "history":
                            RunnableLambda(
                                lambda x: x.get(
                                    "history",
                                    [],
                                )
                            ),

                    }

                    | prompt

                    | self.llm

                    | self.parser

                )

                logging.info(
                    "RAG Chain created."
                )

            return self.chain

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Invoke
    # ==========================================================

    def invoke(

        self,

        question: str,

        history: List[BaseMessage] | None = None,

    ) -> str:

        try:

            response = (

                self.build().invoke(

                    {

                        "question": question,

                        "history": history or [],

                    }

                )

            )

            return response

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Stream
    # ==========================================================

    def stream(

        self,

        question: str,

        history: List[BaseMessage] | None = None,

    ):

        try:

            for chunk in self.build().stream(

                {

                    "question": question,

                    "history": history or [],

                }

            ):

                yield chunk

        except Exception as e:

            raise ChatBotException(e)