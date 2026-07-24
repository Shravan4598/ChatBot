"""
graph/router.py

Production LLM Router.

Responsibilities
----------------
• Decide which tool should answer
• Prefer deterministic routing when possible
• Use Gemini only when necessary
"""

from __future__ import annotations

import json
import re

from core.exception import ChatBotException
from core.logger import logging

from services.llm_service import LLMService

SUPPORTED_TOOLS = {
    "chat",
    "rag",
    "weather",
    "stock",
    "youtube",
    "duckduckgo",
}

YOUTUBE_PATTERN = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com|youtu\.be)/",
    re.IGNORECASE,
)

WEATHER_KEYWORDS = {
    "weather",
    "temperature",
    "forecast",
    "humidity",
    "wind",
    "rain",
    "climate",
}

STOCK_KEYWORDS = {
    "stock",
    "share",
    "market",
    "price",
    "sensex",
    "nifty",
    "nasdaq",
    "dow",
    "nse",
    "bse",
}

SYSTEM_PROMPT = """
You are an AI router.

Choose ONLY ONE tool.

Available tools

chat
rag
weather
stock
youtube
duckduckgo

Rules

- If rag_available=true and the user asks about uploaded documents,
  return rag.

- If rag_available=false,
  never return rag.

- Latest information → duckduckgo

- Weather → weather

- Stocks → stock

- YouTube URL → youtube

- Everything else → chat

Return ONLY JSON.

Example

{"tool":"chat"}
"""

def _parse_json(text: str) -> dict:
    """
    Parse Gemini JSON safely.
    """

    text = text.strip()

    text = text.replace(
        "```json",
        "",
    )

    text = text.replace(
        "```",
        "",
    )

    return json.loads(text)

def _rule_based_router(
    query: str,
    rag_available: bool,
) -> str | None:

    lower = query.lower()

    if YOUTUBE_PATTERN.search(query):
        return "youtube"

    if any(
        word in lower
        for word in WEATHER_KEYWORDS
    ):
        return "weather"

    if any(
        word in lower
        for word in STOCK_KEYWORDS
    ):
        return "stock"

    if rag_available:

        document_words = [

            "document",
            "pdf",
            "docx",
            "txt",
            "file",
            "page",
            "chapter",

        ]

        if any(
            word in lower
            for word in document_words
        ):
            return "rag"

    return None

def route_query(
    query: str,
    rag_available: bool,
) -> str:

    try:

        tool = _rule_based_router(

            query,

            rag_available,

        )

        if tool:

            logging.info(
                "Rule router -> %s",
                tool,
            )

            return tool

        llm = LLMService.get_llm()

        prompt = f"""
{SYSTEM_PROMPT}

rag_available={rag_available}

User:

{query}
"""

        response = llm.invoke(prompt)

        logging.info(
            "Router Response: %s",
            response.content,
        )

        decision = _parse_json(
            response.content
        )

        tool = decision.get(
            "tool",
            "chat",
        ).lower()

        if tool not in SUPPORTED_TOOLS:

            tool = "chat"

        logging.info(
            "LLM Router -> %s",
            tool,
        )

        return tool

    except Exception as e:

        logging.exception(e)

        return "chat"

def router_node(state):

    try:

        state["selected_tool"] = route_query(

            query=state["user_input"],

            rag_available=state[
                "rag_available"
            ],

        )

        return state

    except Exception as e:

        raise ChatBotException(e)

def route_condition(state):

    return state.get(
        "selected_tool",
        "chat",
    )