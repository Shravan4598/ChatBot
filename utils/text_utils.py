# utils/text_utils.py
"""
Text utilities used during ingestion and preprocessing.

Functions:
- join_transcript: join a YouTube transcript (list of segments) into one string.
- clean_text: normalize whitespace, remove control characters, and trim.
"""

from typing import Iterable, List, Dict
import re


def join_transcript(transcript: Iterable[Dict]) -> str:
    """
    Accepts a transcript which is typically a list of dicts returned by
    youtube_transcript_api (each with keys like 'text', 'start', 'duration'),
    and returns a single concatenated string in reading order.

    If transcript items are plain strings, they are concatenated as well.
    """
    if transcript is None:
        return ""

    parts: List[str] = []
    for seg in transcript:
        # seg might be dict-like or string
        if isinstance(seg, dict):
            text = seg.get("text", "")
        else:
            # fallback if library returns simple strings
            text = str(seg)
        if text:
            parts.append(text.strip())
    # join with spaces to avoid accidental word concatenation
    return " ".join(parts)


# Remove multiple whitespace, control characters, and normalize newlines
_CLEAN_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """
    Normalize whitespace, remove control characters, and trim.
    Keeps punctuation and common characters; suitable for feeding to an embedding model or LLM.
    """
    if text is None:
        return ""
    # Replace sequences of whitespace (including newlines, tabs) with single space
    cleaned = _CLEAN_RE.sub(" ", str(text))
    # Trim
    return cleaned.strip()