# rag/youtube_loader.py
"""
rag/youtube_loader.py

Production YouTube Transcript Loader.

Responsibilities
----------------
- Validate YouTube URL
- Download transcript
- Try preferred languages first
- Fall back to auto-generated transcript
- Return LangChain Documents
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

from config.config import settings
from core.exception import ChatBotException
from core.logger import logger

from rag.base_loader import BaseLoader
from utils.text_utils import clean_text, join_transcript
from utils.validators import validate_transcript, validate_youtube_url
from utils.youtube_utils import extract_video_id


class YouTubeLoader(BaseLoader):
    """
    Production-ready YouTube transcript loader.
    """

    def __init__(self) -> None:
        self.languages = settings.TRANSCRIPT_LANGUAGES

    # ---------------------------------------------------------
    @property
    def loader_name(self) -> str:
        return "YouTube Loader"

    # ---------------------------------------------------------
    @property
    def supported_extensions(self) -> List[str]:
        return ["youtube"]

    # ---------------------------------------------------------
    def _fetch_transcript(self, video_id: str) -> tuple[list[dict], str]:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Preferred languages
        for language in self.languages:
            try:
                transcript = transcript_list.find_transcript([language])
                logger.info("Transcript found (%s)", language)
                return (list(transcript.fetch()), language)
            except Exception:
                continue

        # Auto Generated
        for transcript in transcript_list:
            if getattr(transcript, "is_generated", False):
                logger.info("Using generated transcript (%s)", transcript.language_code)
                return (list(transcript.fetch()), transcript.language_code)

        raise NoTranscriptFound(video_id, self.languages, transcript_list)

    # ---------------------------------------------------------
    def load(self, source: str | Path) -> List[Document]:
        """
        Load transcript from YouTube URL.
        """
        try:
            youtube_url = str(source)
            validate_youtube_url(youtube_url)

            video_id = extract_video_id(youtube_url)
            logger.info("Video ID : %s", video_id)

            transcript, language = self._fetch_transcript(video_id)

            transcript_text = join_transcript(transcript)
            transcript_text = clean_text(transcript_text)

            validate_transcript(transcript_text)

            logger.info("Transcript loaded successfully.")

            return [
                Document(
                    page_content=transcript_text,
                    metadata={
                        "document_type": "youtube",
                        "source": youtube_url,
                        "video_id": video_id,
                        "language": language,
                    },
                )
            ]
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise ChatBotException(e)
        except Exception as e:
            raise ChatBotException(e)