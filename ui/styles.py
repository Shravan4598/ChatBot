"""
ui/styles.py

Centralized Streamlit UI styling.

Responsibilities
----------------
• Inject custom CSS
• Style chatbot interface
• Style sidebar
• Improve user experience
"""

from __future__ import annotations

import streamlit as st


# ==========================================================
# Main CSS
# ==========================================================


def load_css() -> None:
    """
    Load application CSS.
    """

    st.markdown(

        """
        <style>


        /* ==================================================
           Global
        ================================================== */

        .block-container {

            padding-top: 2rem;

            padding-bottom: 3rem;

            max-width: 1200px;

        }



        /* ==================================================
           Header
        ================================================== */


        .main-title {

            font-size: 2.5rem;

            font-weight: 700;

            margin-bottom: 0.2rem;

        }


        .subtitle {

            color: #6c757d;

            font-size: 1rem;

        }



        /* ==================================================
           Chat Messages
        ================================================== */


        .stChatMessage {


            border-radius: 18px;

            padding: 12px;

            margin-bottom: 15px;


        }



        [data-testid="stChatMessageAvatarUser"] {

            background-color: #2563eb;

        }



        [data-testid="stChatMessageAvatarAssistant"] {

            background-color: #16a34a;

        }



        /* ==================================================
           Sidebar
        ================================================== */


        section[data-testid="stSidebar"] {


            background-color: #f8fafc;

        }



        .sidebar-title {


            font-size: 1.5rem;

            font-weight: 700;


        }



        .sidebar-section {


            font-size: 1.1rem;

            font-weight: 600;


            margin-top: 15px;


        }



        /* ==================================================
           Buttons
        ================================================== */


        div.stButton > button {


            border-radius: 10px;

            height: 42px;

            font-weight: 600;


        }



        div.stButton > button:hover {


            transform: scale(1.02);


            transition: 0.2s;


        }



        /* ==================================================
           Cards
        ================================================== */


        .info-card {


            padding: 15px;


            border-radius: 15px;


            background: #ffffff;


            border: 1px solid #e5e7eb;


            margin-bottom: 10px;


        }



        .metric-card {


            padding: 10px;


            border-radius: 12px;


            text-align: center;


        }



        /* ==================================================
           Tool Status
        ================================================== */


        .tool-status {


            padding: 10px;


            border-radius: 10px;


            background-color: #eff6ff;


            border-left: 4px solid #2563eb;


        }



        /* ==================================================
           Footer
        ================================================== */


        .footer {


            text-align: center;


            color: #64748b;


            font-size: 0.9rem;


            padding-top: 20px;


        }



        /* ==================================================
           Scrollbar
        ================================================== */


        ::-webkit-scrollbar {


            width: 8px;


        }



        ::-webkit-scrollbar-thumb {


            border-radius: 10px;


        }



        </style>

        """,

        unsafe_allow_html=True,

    )



# ==========================================================
# Header Components
# ==========================================================


def render_header() -> None:
    """
    Render application header.
    """

    st.markdown(

        """
        <div class="main-title">

        🤖 Production AI Assistant

        </div>


        <div class="subtitle">

        LangGraph • Gemini • RAG • Tools • Multi Agent AI

        </div>

        """,

        unsafe_allow_html=True,

    )



# ==========================================================
# Footer
# ==========================================================


def render_footer() -> None:
    """
    Render footer.
    """

    st.markdown(

        """
        <div class="footer">

        Built with ❤️ using LangGraph,
        LangChain and Google Gemini

        </div>

        """,

        unsafe_allow_html=True,

    )