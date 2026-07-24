"""
ui/utils.py

Streamlit Utility Functions.

Responsibilities
----------------
• Session management
• Thread management
• Message formatting
• Chat export
• Common UI helpers
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import streamlit as st

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
)

from core.logger import logging



# ==========================================================
# Thread Utilities
# ==========================================================


def generate_thread_id() -> str:
    """
    Generate unique conversation ID.
    """

    return str(uuid.uuid4())



def initialize_thread() -> None:
    """
    Initialize current thread.
    """


    if "thread_id" not in st.session_state:

        st.session_state.thread_id = (

            generate_thread_id()

        )



# ==========================================================
# Session State Initialization
# ==========================================================


def initialize_session() -> None:
    """
    Initialize Streamlit session variables.
    """


    defaults = {


        "messages": [],


        "thread_id":

            generate_thread_id(),


        "selected_tool":

            None,


        "uploaded_documents":

            [],


        "conversation_loaded":

            False,


        "chat_started":

            False,


    }



    for key, value in defaults.items():


        if key not in st.session_state:


            st.session_state[key] = value



    logging.info(

        "Session initialized."

    )



# ==========================================================
# Message Helpers
# ==========================================================


def add_user_message(
    content: str,
) -> None:
    """
    Add user message.
    """


    st.session_state.messages.append(

        {

            "role":

                "user",


            "content":

                content,


            "timestamp":

                current_time(),

        }

    )



def add_ai_message(
    content: str,
) -> None:
    """
    Add assistant message.
    """


    st.session_state.messages.append(

        {

            "role":

                "assistant",


            "content":

                content,


            "timestamp":

                current_time(),

        }

    )



# ==========================================================
# LangChain Message Conversion
# ==========================================================


def convert_langchain_messages(
    messages: list[BaseMessage],
) -> list[dict]:
    """
    Convert LangChain messages
    into Streamlit format.
    """


    output = []



    for message in messages:


        if isinstance(

            message,

            HumanMessage

        ):


            role = "user"



        elif isinstance(

            message,

            AIMessage

        ):


            role = "assistant"



        else:


            continue



        output.append(

            {

                "role":

                    role,


                "content":

                    message.content,


            }

        )



    return output



# ==========================================================
# Load Conversation
# ==========================================================


def load_messages(
    messages: list[dict],
) -> None:
    """
    Load messages into session.
    """


    st.session_state.messages = messages



# ==========================================================
# Clear Chat
# ==========================================================


def clear_chat() -> None:
    """
    Clear current conversation.
    """


    st.session_state.messages = []


    st.session_state.selected_tool = None


    st.session_state.chat_started = False



# ==========================================================
# Export Chat
# ==========================================================


def export_chat() -> str:
    """
    Convert conversation into text.
    """


    result = []


    for message in st.session_state.messages:


        role = message.get(

            "role",

            "",

        ).upper()



        content = message.get(

            "content",

            "",

        )



        result.append(

            f"""

{role}

{content}

-------------------------

"""

        )



    return "\n".join(result)



# ==========================================================
# Timestamp
# ==========================================================


def current_time() -> str:
    """
    Return formatted timestamp.
    """


    return datetime.now().strftime(

        "%d-%m-%Y %H:%M"

    )



# ==========================================================
# File Size Formatter
# ==========================================================


def format_file_size(
    size: int,
) -> str:
    """
    Convert bytes into readable size.
    """


    if size < 1024:

        return f"{size} B"



    if size < 1024 ** 2:

        return (

            f"{size / 1024:.2f} KB"

        )



    return (

        f"{size / (1024 ** 2):.2f} MB"

    )



# ==========================================================
# Safe String
# ==========================================================


def safe_text(
    value: Any,
) -> str:
    """
    Convert any value safely to string.
    """


    try:

        return str(value)


    except Exception:


        return ""



# ==========================================================
# App Reset
# ==========================================================


def reset_application() -> None:
    """
    Reset complete Streamlit state.
    """


    keys = list(

        st.session_state.keys()

    )


    for key in keys:


        del st.session_state[key]



    st.rerun()