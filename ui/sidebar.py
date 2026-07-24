"""
ui/sidebar.py

Sidebar UI Component.

Responsibilities
----------------
• Render Streamlit sidebar
• Create new chats
• Upload documents
• Show uploaded files
• Show conversation history
• Chat management actions
• Display statistics
"""

from __future__ import annotations

from typing import Callable

import streamlit as st

from services.document_service import DocumentService
from services.chat_service import ChatService
from services.conversation_service import ConversationService

from core.logger import logging



# ==========================================================
# Sidebar Renderer
# ==========================================================


def render_sidebar(
    chat_service: ChatService,
    conversation_service: ConversationService,
) -> None:
    """
    Render complete sidebar.

    Parameters
    ----------
    chat_service:
        Chat service instance.

    conversation_service:
        Conversation service instance.
    """


    with st.sidebar:


        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        st.markdown(

            """
            <div class="sidebar-title">

            🤖 AI Assistant

            </div>

            """,

            unsafe_allow_html=True,

        )


        st.divider()



        # --------------------------------------------------
        # Current Thread
        # --------------------------------------------------

        st.caption(

            f"Thread ID: `{st.session_state.thread_id}`"

        )



        # --------------------------------------------------
        # New Chat
        # --------------------------------------------------

        if st.button(

            "➕ New Chat",

            use_container_width=True,

        ):


            create_new_chat(

                chat_service

            )


        st.divider()



        # --------------------------------------------------
        # Documents
        # --------------------------------------------------

        render_document_section()



        st.divider()



        # --------------------------------------------------
        # Conversations
        # --------------------------------------------------

        render_conversations(

            conversation_service

        )


        st.divider()



        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        render_statistics(

            chat_service

        )



# ==========================================================
# New Chat
# ==========================================================


def create_new_chat(
    chat_service: ChatService,
) -> None:
    """
    Create a fresh conversation.
    """


    st.session_state.thread_id = (

        chat_service.create_thread_id()

    )


    st.session_state.messages = []

    st.session_state.selected_tool = None


    logging.info(

        "New chat created."

    )


    st.rerun()



# ==========================================================
# Document Section
# ==========================================================


def render_document_section():
    """
    Document upload and management.
    """


    st.subheader(
        "📄 Documents"
    )


    uploaded_files = st.file_uploader(

        "Upload Files",

        type=[

            "pdf",

            "docx",

            "txt",

        ],

        accept_multiple_files=True,

    )


    document_service = DocumentService(

        st.session_state.thread_id

    )



    if uploaded_files:


        for uploaded_file in uploaded_files:


            try:


                existing = [

                    f["original_name"]

                    for f in document_service.list_files()

                ]



                if uploaded_file.name in existing:

                    st.info(

                        f"{uploaded_file.name} already exists"

                    )

                    continue



                with st.spinner(

                    f"Uploading {uploaded_file.name}"

                ):


                    document_service.save_file(

                        uploaded_file

                    )


                st.success(

                    f"Uploaded {uploaded_file.name}"

                )



            except Exception as e:


                st.error(

                    str(e)

                )


                logging.exception(e)



    # ------------------------------------------
    # Existing Documents
    # ------------------------------------------


    files = document_service.list_files()



    if files:


        st.markdown(

            "**Uploaded:**"

        )


        for file in files:


            st.write(

                "📄",

                file["name"]

            )


    else:


        st.caption(

            "No documents uploaded."

        )



# ==========================================================
# Conversation History
# ==========================================================


def render_conversations(
    conversation_service: ConversationService,
):
    """
    Show previous conversations.
    """


    st.subheader(

        "💬 History"

    )


    conversations = (

        conversation_service.list_conversations()

    )



    if not conversations:


        st.caption(

            "No previous chats."

        )

        return



    for conversation in conversations:


        thread_id = conversation.get(

            "thread_id"

        )


        title = conversation.get(

            "title",

            "New Chat"

        )



        if st.button(

            title,

            key=f"conversation-{thread_id}",

            use_container_width=True,

        ):


            st.session_state.thread_id = thread_id


            st.session_state.messages = (

                conversation_service.get_messages(

                    thread_id

                )

            )


            st.rerun()



# ==========================================================
# Statistics
# ==========================================================


def render_statistics(
    chat_service: ChatService,
):
    """
    Display chatbot statistics.
    """


    st.subheader(

        "📊 Statistics"

    )


    try:


        stats = chat_service.statistics()



        col1, col2 = st.columns(2)



        with col1:


            st.metric(

                "Chats",

                stats.get(

                    "conversations",

                    0

                ),

            )



        with col2:


            st.metric(

                "Threads",

                stats.get(

                    "threads",

                    0

                ),

            )



    except Exception as e:


        st.caption(

            "Statistics unavailable."

        )

        logging.exception(e)