"""
ui/components.py

Reusable Streamlit UI Components.

Responsibilities
----------------
• Render cards
• Render badges
• Render metrics
• Render documents
• Render RAG sources
• Render notifications
"""

from __future__ import annotations

from typing import Any

import streamlit as st



# ==========================================================
# Tool Badge
# ==========================================================


def tool_badge(
    tool_name: str,
) -> None:
    """
    Display selected tool badge.
    """


    tools = {

        "rag":
            (
                "📚 RAG",
                "Document Search"
            ),

        "weather":
            (
                "🌤 Weather",
                "Live Weather"
            ),

        "stock":
            (
                "📈 Stock",
                "Market Data"
            ),

        "youtube":
            (
                "▶️ YouTube",
                "Video Analysis"
            ),

        "duckduckgo":
            (
                "🔎 Web Search",
                "Internet Search"
            ),

        "chat":
            (
                "🤖 Gemini",
                "AI Chat"
            ),

    }



    title, description = tools.get(

        tool_name,

        (
            "🔧 Tool",
            tool_name
        )

    )


    st.markdown(

        f"""

        <div class="info-card">

        <b>{title}</b>

        <br>

        <small>{description}</small>

        </div>

        """,

        unsafe_allow_html=True,

    )



# ==========================================================
# Document Card
# ==========================================================


def document_card(
    document: dict[str, Any],
) -> None:
    """
    Display uploaded document information.
    """


    name = document.get(

        "original_name",

        document.get(

            "name",

            "Unknown"

        )

    )


    size = document.get(

        "size",

        0

    )



    size_kb = round(

        size / 1024,

        2

    )



    st.markdown(

        f"""

        <div class="info-card">


        📄 <b>{name}</b>

        <br>


        Size:

        {size_kb} KB


        </div>


        """,

        unsafe_allow_html=True,

    )



# ==========================================================
# Document List
# ==========================================================


def document_list(
    documents: list[dict],
) -> None:
    """
    Display multiple documents.
    """


    if not documents:


        empty_state(

            "📂 No documents uploaded"

        )

        return



    for document in documents:

        document_card(

            document

        )



# ==========================================================
# Metrics Card
# ==========================================================


def metric_card(
    title: str,
    value: Any,
) -> None:
    """
    Display single metric.
    """


    st.markdown(

        f"""

        <div class="metric-card">


        <h3>{value}</h3>


        <p>{title}</p>


        </div>


        """,

        unsafe_allow_html=True,

    )



# ==========================================================
# Dashboard Metrics
# ==========================================================


def metrics_row(
    metrics: dict,
) -> None:
    """
    Display multiple metrics.
    """


    columns = st.columns(

        len(metrics)

    )


    for column, (key, value) in zip(

        columns,

        metrics.items(),

    ):


        with column:


            metric_card(

                key,

                value

            )



# ==========================================================
# RAG Sources
# ==========================================================


def rag_sources(
    sources: list,
) -> None:
    """
    Display retrieved document chunks.
    """


    if not sources:

        return



    st.subheader(

        "📚 Sources"

    )



    for index, source in enumerate(

        sources,

        start=1

    ):



        metadata = getattr(

            source,

            "metadata",

            {}

        )


        content = getattr(

            source,

            "page_content",

            ""

        )



        with st.expander(

            f"Source {index}"

        ):



            st.write(

                content[:500]

            )


            if metadata:


                st.json(

                    metadata

                )



# ==========================================================
# Loading Component
# ==========================================================


def loading_message(
    text: str = "Processing..."
):
    """
    Show loading message.
    """


    return st.status(

        text,

        expanded=True,

    )



# ==========================================================
# Notifications
# ==========================================================


def success_message(
    message: str,
) -> None:
    """
    Success notification.
    """


    st.success(

        message

    )



def error_message(
    message: str,
) -> None:
    """
    Error notification.
    """


    st.error(

        message

    )



def info_message(
    message: str,
) -> None:
    """
    Information notification.
    """


    st.info(

        message

    )



# ==========================================================
# Empty State
# ==========================================================


def empty_state(
    message: str,
) -> None:
    """
    Display empty UI state.
    """


    st.markdown(

        f"""

        <div class="info-card">


        {message}


        </div>


        """,

        unsafe_allow_html=True,

    )



# ==========================================================
# Chat Statistics
# ==========================================================


def chatbot_status(
    status: dict,
) -> None:
    """
    Display chatbot health.
    """


    st.subheader(

        "🟢 System Status"

    )



    metrics_row(

        {

            "LLM":

            status.get(

                "llm",

                "Gemini"

            ),


            "RAG":

            status.get(

                "rag",

                "Ready"

            ),


            "Tools":

            status.get(

                "tools",

                0

            ),

        }

    )