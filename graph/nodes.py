"""
graph/nodes.py

Production LangGraph Nodes

Responsibilities
----------------
• Router Node
• Chat Node
• RAG Node
• Tool Nodes
• Final Node
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from core.exception import ChatBotException
from core.logger import logging

from graph.router import route_query

from rag.rag_service import RAGService

from services.llm_service import LLMService

from tools.weather_tool import WeatherTool
from tools.stock_tool import StockTool
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.youtube_tool import YouTubeTool


# ==========================================================
# Helpers
# ==========================================================

def _append_ai_message(
    state: dict,
    content: str,
) -> dict:
    """
    Append assistant response to history.
    """

    state["messages"].append(
        AIMessage(content=content)
    )

    state["final_response"] = content

    return state


def _run_tool(
    state: dict,
    tool,
) -> dict:
    """
    Execute any tool and update state.
    """

    result = tool.run(
        state["user_input"]
    )

    state["tool_output"] = result

    return _append_ai_message(
        state,
        result,
    )


# ==========================================================
# Router
# ==========================================================

def router_node(state: dict):
    """
    Decide which tool should answer.
    """

    try:

        tool = route_query(

            query=state["user_input"],

            rag_available=state["rag_available"],

        )

        state["selected_tool"] = tool

        logging.info(
            "Router selected tool: %s",
            tool,
        )

        return state

    except Exception as e:

        raise ChatBotException(e)


# ==========================================================
# Chat
# ==========================================================

def chat_node(state: dict):
    """
    General Gemini conversation.
    """

    try:

        llm = LLMService.get_llm()

        response = llm.invoke(
            state["messages"]
        )

        return _append_ai_message(

            state,

            response.content,

        )

    except Exception as e:

        raise ChatBotException(e)


# ==========================================================
# RAG
# ==========================================================

def rag_node(state: dict):
    """
    Answer from uploaded documents.
    """

    try:

        rag = RAGService.get_instance(
            thread_id=state["thread_id"]
        )

        answer = rag.ask(

            question=state["user_input"],

            history=state["messages"],

        )

        logging.info(
            "RAG response generated."
        )

        return _append_ai_message(

            state,

            answer,

        )

    except Exception as e:

        raise ChatBotException(e)

# ==========================================================
# Weather
# ==========================================================

def weather_node(state: dict):
    """
    Weather Tool Node.
    """

    try:

        logging.info(
            "Executing Weather Tool..."
        )

        return _run_tool(
            state,
            WeatherTool(),
        )

    except Exception as e:

        raise ChatBotException(e)


# ==========================================================
# Stock
# ==========================================================

def stock_node(state: dict):
    """
    Stock Tool Node.
    """

    try:

        logging.info(
            "Executing Stock Tool..."
        )

        return _run_tool(
            state,
            StockTool(),
        )

    except Exception as e:

        raise ChatBotException(e)


# ==========================================================
# DuckDuckGo
# ==========================================================

def duckduckgo_node(state: dict):
    """
    Web Search Tool Node.
    """

    try:

        logging.info(
            "Executing DuckDuckGo Tool..."
        )

        return _run_tool(
            state,
            DuckDuckGoTool(),
        )

    except Exception as e:

        raise ChatBotException(e)


# ==========================================================
# YouTube
# ==========================================================

def youtube_node(state: dict):
    """
    YouTube Tool Node.
    """

    try:

        logging.info(
            "Executing YouTube Tool..."
        )

        return _run_tool(
            state,
            YouTubeTool(),
        )

    except Exception as e:

        raise ChatBotException(e)


# ==========================================================
# Final
# ==========================================================

def final_node(state: dict):
    """
    Final node executed before END.

    Responsible for logging the workflow completion
    and returning the updated state.
    """

    logging.info(

        "Workflow completed | Thread=%s | Tool=%s",

        state.get("thread_id"),

        state.get("selected_tool"),

    )

    return state