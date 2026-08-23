"""
tools/youtube_tool.py

Production YouTube Tool.

Responsibilities
----------------
- Process YouTube videos
- Build transcript RAG pipeline
- Answer questions about the video
- Generate video summaries
"""

from __future__ import annotations

from core.exception import ChatBotException
from core.logger import logging

from tools.base_tool import BaseTool

# Import your existing production pipeline
from src.pipeline.rag_pipeline import RAGPipeline


class YouTubeTool(BaseTool):
    """
    Production YouTube Tool.
    """

    def __init__(self) -> None:

        self.pipeline = RAGPipeline()

        logging.info(
            "YouTube Tool initialized."
        )

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:

        return "youtube_tool"

    @property
    def description(self) -> str:

        return (
            "Summarize YouTube videos and answer "
            "questions using video transcripts."
        )

    # ==========================================================
    # Build
    # ==========================================================

    def build(
        self,
        youtube_url: str,
    ) -> dict:

        try:

            logging.info(
                "Building YouTube pipeline..."
            )

            self.pipeline.build(
                youtube_url
            )

            logging.info(
                "Pipeline built successfully."
            )

            return {

                "status": "success",

                "message":
                    "Transcript indexed successfully.",

            }

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Ask
    # ==========================================================

    def invoke(
        self,
        question: str,
    ) -> str:

        try:

            return self.pipeline.ask(
                question
            )

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Summary
    # ==========================================================

    def summarize(
        self,
    ) -> str:
        """
        Generate a complete summary.
        """

        summary_prompt = """

Summarize this YouTube video.

Include

1. Overview

2. Main Topics

3. Important Concepts

4. Key Takeaways

5. Action Items

6. Important Timestamps if available.

"""

        return self.invoke(
            summary_prompt
        )

    # ==========================================================
    # Key Points
    # ==========================================================

    def key_points(
        self,
    ) -> str:

        return self.invoke(

            "Give the important key points "
            "from this video."

        )

    # ==========================================================
    # Action Items
    # ==========================================================

    def action_items(
        self,
    ) -> str:

        return self.invoke(

            "List all action items from the video."

        )

    # ==========================================================
    # Reset
    # ==========================================================

    def reset(
        self,
    ) -> None:

        self.pipeline.reset()

        logging.info(
            "YouTube pipeline reset."
        )

    # ==========================================================
    # Status
    # ==========================================================

    @property
    def ready(self) -> bool:

        return self.pipeline.is_ready