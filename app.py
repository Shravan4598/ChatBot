"""
app.py

Production Streamlit ChatBot

Features
--------
✓ LangGraph
✓ Gemini
✓ RAG
✓ Weather
✓ Stock
✓ DuckDuckGo Search
✓ YouTube Summary
✓ Conversation Memory
✓ Streaming Response
✓ Multi Document Upload
✓ Thread Management
"""


from __future__ import annotations


import streamlit as st


from services.chat_service import ChatService
from services.conversation_service import ConversationService


from ui.styles import (
    load_css,
    render_header,
    render_footer,
)


from ui.sidebar import (
    render_sidebar,
)


from ui.chat import (
    render_chat,
)


from ui.utils import (
    initialize_session,
)


from core.logger import logging



# ==========================================================
# Page Configuration
# ==========================================================


st.set_page_config(

    page_title="Production AI Assistant",

    page_icon="🤖",

    layout="wide",

    initial_sidebar_state="expanded",

)



# ==========================================================
# Load UI Theme
# ==========================================================


load_css()



# ==========================================================
# Session Initialization
# ==========================================================


initialize_session()



# ==========================================================
# Service Initialization
# ==========================================================


@st.cache_resource
def get_chat_service():

    """
    Create singleton ChatService.
    """

    logging.info(

        "Creating ChatService instance."

    )

    return ChatService()



@st.cache_resource
def get_conversation_service():

    """
    Create singleton ConversationService.
    """

    logging.info(

        "Creating ConversationService instance."

    )

    return ConversationService()



chat_service = get_chat_service()


conversation_service = (
    get_conversation_service()
)



# ==========================================================
# Header
# ==========================================================


render_header()



# ==========================================================
# Sidebar
# ==========================================================


render_sidebar(

    chat_service,

    conversation_service,

)



# ==========================================================
# Main Chat Interface
# ==========================================================


try:


    render_chat(

        chat_service

    )


except Exception as e:


    logging.exception(e)


    st.error(

        "⚠️ Something went wrong while running chatbot."

    )



# ==========================================================
# Footer
# ==========================================================


render_footer()