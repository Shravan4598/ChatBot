"""
ui/chat.py

Chat UI Component.

Responsibilities
----------------
• Render conversation messages
• Handle user input
• Stream chatbot responses
• Display tool usage
• Manage chat state
"""

from __future__ import annotations

from typing import Generator
import streamlit as st

from services.chat_service import ChatService

from core.logger import logging
from core.exception import ChatBotException


# ==========================================================
# Render Chat History
# ==========================================================
def render_chat_history() -> None:
    """
    Display previous messages.
    """
    # Ensure session state keys exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        with st.chat_message(role):
            # Use markdown by default; if you want raw text, use st.write(content)
            st.markdown(content)


# ==========================================================
# Tool Status UI
# ==========================================================
def render_tool_status(tool_name: str):
    """
    Display active tool information.
    """
    tool_messages = {
        "rag": "📚 Searching uploaded documents",
        "weather": "🌤 Fetching weather information",
        "stock": "📈 Fetching stock market data",
        "duckduckgo": "🔎 Searching web",
        "youtube": "▶️ Processing YouTube video",
        "chat": "🤖 Generating response",
        "document": "📁 Processing document",
    }

    return st.info(tool_messages.get(tool_name, f"🔧 Using {tool_name}"))


# ==========================================================
# Stream Response
# ==========================================================
def stream_chat_response(chat_service: ChatService, user_input: str) -> str:
    """
    Stream response from LangGraph.

    Returns
    -------
    str
        Final generated response.
    """
    try:
        final_response = ""
        tool_box = None

        # Create a placeholder that will render inside the assistant chat bubble.
        message_placeholder = st.empty()

        # Stream events from the chat service.
        # The stream yields dict events that contain 'type' keys (e.g., "tool", "text").
        for event in chat_service.stream(user_input, st.session_state.thread_id):
            # Defensive: log the entire event so we can debug what the graph yields.
            logging.info("Stream event: %s", repr(event))

            # Some backends may yield plain strings; handle that.
            if isinstance(event, str):
                final_response += event
                message_placeholder.markdown(final_response + "▌")
                continue

            # Expect event to be a dict
            if not isinstance(event, dict):
                continue

            # Tool event (indicates which tool is currently active)
            if event.get("type") == "tool":
                tool_name = event.get("tool", "unknown")
                st.session_state.selected_tool = tool_name
                # Show a small info box indicating the tool is active
                tool_box = render_tool_status(tool_name)

            # Text event (chunk)
            elif event.get("type") == "text":
                content = event.get("content", "") or ""
                final_response += content
                # Show partial with caret to indicate streaming
                message_placeholder.markdown(final_response + "▌")

            # Optional: handle other event types (e.g., "error", "meta")
            elif event.get("type") == "error":
                err_msg = event.get("message", "Unknown error")
                logging.warning("Received error event from stream: %s", err_msg)
                message_placeholder.markdown(f"**Error:** {err_msg}")
                break

        # Finalize message (replace caret with final text)
        if final_response:
            message_placeholder.markdown(final_response)
        else:
            # If we got no text events, show a friendly notice and log details
            logging.info("No text events received from stream for input: %s", user_input)
            message_placeholder.info("No response generated. Check logs for details.")

        # Clear tool UI if present
        if tool_box:
            tool_box.empty()

        return final_response

    except Exception as e:
        logging.exception(e)
        raise ChatBotException(e)


# ==========================================================
# Main Chat Renderer
# ==========================================================
def render_chat(chat_service: ChatService) -> None:
    """
    Main chat UI renderer.
    """
    # Initialize session state defaults used by the UI
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = "default"
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = None

    # ------------------------------------------
    # Existing Messages
    # ------------------------------------------
    render_chat_history()

    # ------------------------------------------
    # User Input
    # ------------------------------------------
    user_input = st.chat_input("Ask anything...")

    if not user_input:
        return

    # ------------------------------------------
    # Append user message to history and show it
    # ------------------------------------------
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ------------------------------------------
    # Assistant (streaming)
    # ------------------------------------------
    with st.chat_message("assistant"):
        try:
            answer = stream_chat_response(chat_service, user_input)

            # Append assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            error = " Error: " + str(e)
            st.error(error)
            logging.exception(e)