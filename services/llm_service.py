"""
services/llm_service.py

Centralized Gemini LLM service.

This module exposes a singleton Gemini model that can be reused
throughout the application. It avoids repeatedly initializing
the LLM and provides helper methods for accessing model
configuration.
"""

from __future__ import annotations

from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging


class LLMService:
    """
    Singleton wrapper around ChatGoogleGenerativeAI.
    """

    _instance: Optional[ChatGoogleGenerativeAI] = None

    @classmethod
    def get_llm(cls) -> ChatGoogleGenerativeAI:
        """
        Return a singleton Gemini LLM instance.
        """

        try:

            if cls._instance is None:

                logging.info(
                    "Initializing Gemini Model: %s",
                    settings.GEMINI_MODEL,
                )

                
                cls._instance = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=settings.TEMPERATURE,
                    max_output_tokens=settings.MAX_OUTPUT_TOKENS,
                    top_p=settings.GEMINI_TOP_P,
                    top_k=settings.GEMINI_TOP_K,
                    timeout=settings.REQUEST_TIMEOUT,
                    max_retries=settings.MAX_RETRIES,
                    streaming=True,
                )

                logging.info("Gemini model initialized successfully.")

            return cls._instance

        except Exception as e:
            raise ChatBotException(e)

    @classmethod
    def reset(cls) -> None:
        """
        Reset singleton instance.

        Mainly useful during testing.
        """

        cls._instance = None

        logging.info("LLM singleton reset.")

    @classmethod
    def model_name(cls) -> str:
        """
        Return current model name.
        """

        return settings.GEMINI_MODEL

    @classmethod
    def model_info(cls) -> dict:
        """
        Return model configuration.
        """

        return {
            "model": settings.GEMINI_MODEL,
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
            "top_p": settings.GEMINI_TOP_P,
            "top_k": settings.GEMINI_TOP_K,
            "timeout": settings.REQUEST_TIMEOUT,
            "max_retries": settings.MAX_RETRIES,
            "streaming": True,
        }
    @classmethod
    def stream_response(
        cls,
        messages,
    ):
        """
        Stream Gemini response token by token.
        """

        try:

            llm = cls.get_llm()

            for chunk in llm.stream(messages):

                if chunk.content:

                    yield chunk.content


        except Exception as e:

            raise ChatBotException(e)