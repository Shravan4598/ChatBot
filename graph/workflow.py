"""
graph/workflow.py

Production LangGraph Workflow.

Responsibilities
----------------
• Build the LangGraph workflow
• Register nodes
• Register conditional routing
• Configure checkpointing
• Compile the graph
"""

from __future__ import annotations

from langgraph.graph import (
    START,
    END,
    StateGraph,
)

from core.exception import ChatBotException
from core.logger import logging

from graph.state import ChatState

from graph.router import (
    route_condition,
)

from graph.nodes import (
    router_node,
    chat_node,
    rag_node,
    weather_node,
    stock_node,
    duckduckgo_node,
    youtube_node,
    final_node,
)

from services.checkpoint_service import (
    CheckpointService,
)


class ChatbotWorkflow:
    """
    Production LangGraph workflow.
    """

    _compiled_graph = None

    def __init__(self):

        logging.info(
            "Initializing LangGraph Workflow..."
        )

        self.builder = StateGraph(
            ChatState
        )

        self._build()

    # =====================================================
    # Build
    # =====================================================

    def _build(self):

        self._add_nodes()

        self._add_edges()

    # =====================================================
    # Nodes
    # =====================================================

    def _add_nodes(self):

        self.builder.add_node(
            "router",
            router_node,
        )

        self.builder.add_node(
            "chat",
            chat_node,
        )

        self.builder.add_node(
            "rag",
            rag_node,
        )

        self.builder.add_node(
            "weather",
            weather_node,
        )

        self.builder.add_node(
            "stock",
            stock_node,
        )

        self.builder.add_node(
            "duckduckgo",
            duckduckgo_node,
        )

        self.builder.add_node(
            "youtube",
            youtube_node,
        )

        self.builder.add_node(
            "final",
            final_node,
        )

    # =====================================================
    # Edges
    # =====================================================

    def _add_edges(self):

        self.builder.add_edge(
            START,
            "router",
        )

        self.builder.add_conditional_edges(

            "router",

            route_condition,

            {

                "chat": "chat",

                "rag": "rag",

                "weather": "weather",

                "stock": "stock",

                "duckduckgo": "duckduckgo",

                "youtube": "youtube",

            },

        )

        self.builder.add_edge(
            "chat",
            "final",
        )

        self.builder.add_edge(
            "rag",
            "final",
        )

        self.builder.add_edge(
            "weather",
            "final",
        )

        self.builder.add_edge(
            "stock",
            "final",
        )

        self.builder.add_edge(
            "duckduckgo",
            "final",
        )

        self.builder.add_edge(
            "youtube",
            "final",
        )

        self.builder.add_edge(
            "final",
            END,
        )

    # =====================================================
    # Compile
    # =====================================================

    def get_graph(self):

        try:

            if self.__class__._compiled_graph:

                return self.__class__._compiled_graph

            checkpoint = (
                CheckpointService()
                .get_checkpointer()
            )

            graph = self.builder.compile(

                checkpointer=checkpoint,

            )

            self.__class__._compiled_graph = graph

            logging.info(
                "LangGraph compiled successfully."
            )

            return graph

        except Exception as e:

            raise ChatBotException(e)