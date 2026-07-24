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


    for message in st.session_state.messages:


        role = message.get(

            "role",

            "assistant",

        )


        content = message.get(

            "content",

            "",

        )


        with st.chat_message(role):

            st.markdown(content)



# ==========================================================
# Tool Status UI
# ==========================================================


def render_tool_status(
    tool_name: str,
):
    """
    Display active tool information.
    """


    tool_messages = {

        "rag":
            "📚 Searching uploaded documents",

        "weather":
            "🌤 Fetching weather information",

        "stock":
            "📈 Fetching stock market data",

        "duckduckgo":
            "🔎 Searching web",

        "youtube":
            "▶️ Processing YouTube video",

        "chat":
            "🤖 Generating response",

    }


    return st.info(

        tool_messages.get(

            tool_name,

            f"🔧 Using {tool_name}"

        )

    )



# ==========================================================
# Stream Response
# ==========================================================


def stream_chat_response(
    chat_service: ChatService,
    user_input: str,
) -> str:
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


        response_box = st.empty()



        for event in chat_service.stream(

            user_input,

            st.session_state.thread_id,

        ):



            # ---------------------------------
            # Tool event
            # ---------------------------------


            if event.get(

                "type"

            ) == "tool":


                tool_name = event.get(

                    "tool",

                    "unknown"

                )


                st.session_state.selected_tool = tool_name



                tool_box = render_tool_status(

                    tool_name

                )



            # ---------------------------------
            # Text event
            # ---------------------------------


            elif event.get(

                "type"

            ) == "text":


                content = event.get(

                    "content",

                    "",

                )


                final_response += content



                response_box.markdown(

                    final_response + "▌"

                )



        response_box.markdown(

            final_response

        )


        if tool_box:

            tool_box.empty()



        return final_response



    except Exception as e:


        logging.exception(e)

        raise ChatBotException(e)



# ==========================================================
# Main Chat Renderer
# ==========================================================


def render_chat(
    chat_service: ChatService,
) -> None:
    """
    Main chat UI renderer.
    """


    # ------------------------------------------
    # Existing Messages
    # ------------------------------------------


    render_chat_history()



    # ------------------------------------------
    # User Input
    # ------------------------------------------


    user_input = st.chat_input(

        "Ask anything..."

    )



    if not user_input:

        return



    # ------------------------------------------
    # User Message
    # ------------------------------------------


    st.session_state.messages.append(

        {

            "role":

                "user",


            "content":

                user_input,

        }

    )



    with st.chat_message(

        "user"

    ):

        st.markdown(

            user_input

        )



    # ------------------------------------------
    # Assistant
    # ------------------------------------------


    with st.chat_message(

        "assistant"

    ):


        try:


            answer = stream_chat_response(

                chat_service,

                user_input,

            )


            st.session_state.messages.append(

                {

                    "role":

                        "assistant",


                    "content":

                        answer,

                }

            )



        except Exception as e:


            error = (

                " Error: "

                + str(e)

            )


            st.error(error)



            logging.exception(e)