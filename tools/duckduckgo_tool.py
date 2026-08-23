"""
tools/duckduckgo_tool.py

DuckDuckGo Search Tool.

Responsibilities
----------------
- Search the web
- Return structured search results
- Support LangGraph tool routing
"""

from __future__ import annotations

from typing import Any

from langchain_community.tools import DuckDuckGoSearchResults

from core.exception import ChatBotException
from core.logger import logging

from tools.base_tool import BaseTool


class DuckDuckGoTool(BaseTool):
    """
    DuckDuckGo Search Tool.
    """

    def __init__(self) -> None:

        self.search = DuckDuckGoSearchResults(
            output_format="list",
            max_results=5,
        )

        logging.info(
            "DuckDuckGo Tool initialized."
        )

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:

        return "duckduckgo_search"

    @property
    def description(self) -> str:

        return (
            "Search the internet for the latest "
            "news, facts, events, and general information."
        )

    # ==========================================================
    # Search
    # ==========================================================

    def invoke(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Perform a DuckDuckGo search.

        Parameters
        ----------
        query : str
            Search query.

        max_results : int
            Maximum number of results.

        Returns
        -------
        list[dict]
        """

        try:

            logging.info(
                "Searching DuckDuckGo : %s",
                query,
            )

            self.search.max_results = max_results

            results = self.search.invoke(query)

            logging.info(
                "%d search result(s) found.",
                len(results),
            )

            return results

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Summary
    # ==========================================================

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict]:

        return self.invoke(
            query=query,
            max_results=max_results,
        )