# graph/state.py
"""
Shared LangGraph state.

This module defines the state that flows through every
LangGraph node.
"""

from __future__ import annotations

from typing import Annotated, Any, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    Shared application state.

    Every LangGraph node receives this state
    and returns updated values.
    """

    # ==========================================================
    # Chat Messages
    # ==========================================================
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    # ==========================================================
    # User Input
    # ==========================================================
    user_input: str

    # ==========================================================
    # Thread / Session
    # ==========================================================
    thread_id: str

    # ==========================================================
    # Tool Routing
    # ==========================================================
    selected_tool: Optional[str]
    tool_input: Optional[Any]
    tool_output: Optional[Any]

    # ==========================================================
    # Uploaded Documents
    # ==========================================================
    uploaded_files: list[str]

    # ==========================================================
    # Current Active Document
    # ==========================================================
    active_document: Optional[str]

    # ==========================================================
    # Current YouTube Video
    # ==========================================================
    youtube_url: Optional[str]

    # ==========================================================
    # RAG
    # ==========================================================
    rag_available: bool

    # ==========================================================
    # Metadata
    # ==========================================================
    metadata: dict[str, Any]

    # ==========================================================
    # Final Response
    # ==========================================================
    final_response: str


# Backwards / external compatibility:
# Some modules expect ChatState to be defined. Provide ChatState as an alias
# to the TypedDict above so imports like "from graph.state import ChatState"
# succeed without changing other code.
ChatState = GraphState

# Export names
__all__ = ["GraphState", "ChatState"]