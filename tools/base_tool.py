"""
tools/base_tool.py

Abstract base class for all chatbot tools.

Responsibilities
----------------
- Define a common interface for every tool.
- Ensure consistency across implementations.
- Make tool registration and routing easier.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Abstract base class for all chatbot tools.
    """

    # ==========================================================
    # Tool Information
    # ==========================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique tool name.

        Example:
            weather_tool
            stock_tool
            rag_tool
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of the tool.
        """
        raise NotImplementedError

    # ==========================================================
    # Tool Execution
    # ==========================================================

    @abstractmethod
    def invoke(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the tool.

        Returns
        -------
        Any
            Tool-specific response.
        """
        raise NotImplementedError

    # ==========================================================
    # Utility
    # ==========================================================

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Allow direct callable usage.

        Example:
            tool(query="Python")
        """

        return self.invoke(
            *args,
            **kwargs,
        )

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}')"
        )