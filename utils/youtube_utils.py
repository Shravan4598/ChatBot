# utils/youtube_utils.py
"""
YouTube helper utilities.

- extract_video_id(url): returns the video id (v=...) or short id from youtu.be URLs.
"""

from urllib.parse import urlparse, parse_qs
from core.exception import ChatBotException


def extract_video_id(url: str) -> str:
    """
    Extract the YouTube video id from common URL forms:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - with additional query params

    Returns the video id string. Raises ChatBotException if extraction fails.
    """
    if not url or not isinstance(url, str):
        raise ChatBotException(ValueError("Invalid URL provided for video id extraction."))

    url = url.strip()

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ChatBotException(e)

    # youtu.be short links: path is /VIDEOID
    host = parsed.netloc.lower()
    path = parsed.path or ""

    if "youtu.be" in host:
        # path like "/VIDEOID"
        video_id = path.lstrip("/")
        if video_id:
            return video_id
        raise ChatBotException(ValueError(f"Could not extract video id from URL: {url}"))

    # youtube.com: look for v= query param
    if "youtube.com" in host:
        qs = parse_qs(parsed.query)
        v = qs.get("v")
        if v and len(v) > 0:
            return v[0]
        # sometimes the URL can be a /embed/VIDEOID or /v/VIDEOID
        parts = path.split("/")
        for i, part in enumerate(parts):
            if part in ("embed", "v") and i + 1 < len(parts):
                candidate = parts[i + 1]
                if candidate:
                    return candidate
    # fallback: if last path segment looks like an id
    # (not guaranteed but useful)
    last_segment = path.rstrip("/").split("/")[-1]
    if last_segment:
        return last_segment

    raise ChatBotException(ValueError(f"Unable to extract YouTube video id from URL: {url}"))