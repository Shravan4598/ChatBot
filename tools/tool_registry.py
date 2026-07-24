from tools.rag_tool import RAGTool
"""
tools/tool_registry.py

Production Tool Registry.

Responsibilities
----------------
- Register all chatbot tools
- Retrieve tools by name
- Return all registered tools
- Support LangGraph routing
"""

from __future__ import annotations

from typing import Dict, List

from core.exception import ChatBotException
from core.logger import logging

from tools.base_tool import BaseTool
from tools.duckduckgo_tool import DuckDuckGoTool
from tools.stock_tool import StockTool
from tools.weather_tool import WeatherTool
from tools.youtube_tool import YouTubeTool


class ToolRegistry:
    """
    Registry for chatbot tools.

    Singleton-style registry used throughout
    the application.
    """

    _tools: Dict[str, BaseTool] = {}

    # ==========================================================
    # Register
    # ==========================================================

    @classmethod
    def register(
        cls,
        tool: BaseTool,
    ) -> None:
        """
        Register a tool.
        """

        try:

            cls._tools[tool.name] = tool

            logging.info(
                "Registered tool: %s",
                tool.name,
            )

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Register Default Tools
    # ==========================================================

    @classmethod
    def register_default_tools(
        cls,
    ) -> None:
        """
        Register all built-in tools.
        """

        cls.register(
            DuckDuckGoTool()
        )

        cls.register(
            WeatherTool()
        )

        cls.register(
            StockTool()
        )

        cls.register(
            YouTubeTool()
        )
        cls.register(
            RAGTool()
        )

        logging.info(
            "Default tools registered."
        )

    # ==========================================================
    # Get Tool
    # ==========================================================

    @classmethod
    def get_tool(
        cls,
        name: str,
    ) -> BaseTool:
        """
        Return tool by name.
        """

        try:

            return cls._tools[name]

        except KeyError:

            raise ValueError(
                f"Tool '{name}' is not registered."
            )

    # ==========================================================
    # Exists
    # ==========================================================

    @classmethod
    def has_tool(
        cls,
        name: str,
    ) -> bool:

        return name in cls._tools

    # ==========================================================
    # List
    # ==========================================================

    @classmethod
    def list_tools(
        cls,
    ) -> List[str]:

        return list(
            cls._tools.keys()
        )

    # ==========================================================
    # Return All
    # ==========================================================

    @classmethod
    def get_all_tools(
        cls,
    ) -> Dict[str, BaseTool]:

        return cls._tools

    # ==========================================================
    # Remove
    # ==========================================================

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> None:

        if name in cls._tools:

            del cls._tools[name]

            logging.info(
                "Removed tool: %s",
                name,
            )

    # ==========================================================
    # Reset
    # ==========================================================

    @classmethod
    def clear(
        cls,
    ) -> None:

        cls._tools.clear()

        logging.info(
            "Tool registry cleared."
        )