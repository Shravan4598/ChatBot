# utils/validators.py
"""
Validators used across loaders and ingestion modules.

- validate_youtube_url(url): raises ChatBotException if URL invalid.
- validate_transcript(text): raises ChatBotException if transcript is empty or too short.
"""

from typing import Optional
import re
from urllib.parse import urlparse, parse_qs

from core.exception import ChatBotException


YOUTUBE_DOMAINS = ("youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be")

# simple youtube URL regex for quick check (not exhaustive)
_YT_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
    flags=re.IGNORECASE,
)


def validate_youtube_url(url: str) -> bool:
    """
    Basic validation of a YouTube URL. Raises ChatBotException on failure.
    Returns True if URL looks valid.
    """
    if not url or not isinstance(url, str):
        raise ChatBotException(ValueError("YouTube URL must be a non-empty string."))

    url = url.strip()
    if _YT_REGEX.match(url):
        return True

    # Try parsing and checking netloc
    try:
        parsed = urlparse(url)
        if parsed.netloc and any(d in parsed.netloc.lower() for d in YOUTUBE_DOMAINS):
            return True
    except Exception:
        pass

    raise ChatBotException(ValueError(f"Invalid YouTube URL: {url}"))


def validate_transcript(text: Optional[str], min_length: int = 20) -> bool:
    """
    Ensures transcript has meaningful content. Raises ChatBotException on failure.

    - min_length: smallest allowed length in characters
    """
    if text is None:
        raise ChatBotException(ValueError("Transcript is empty or unavailable."))

    # strip whitespace and check length
    t = str(text).strip()
    if len(t) < min_length:
        raise ChatBotException(ValueError("Transcript too short or empty."))

    return True