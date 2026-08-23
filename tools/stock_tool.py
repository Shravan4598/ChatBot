"""
tools/stock_tool.py

Production Stock Tool.

Responsibilities
----------------
- Fetch real-time stock data
- Normalize API response
- Handle API errors gracefully
"""

from __future__ import annotations

from typing import Any

import requests

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging

from tools.base_tool import BaseTool


class StockTool(BaseTool):
    """
    Production Stock Tool using Alpha Vantage API.
    """

    BASE_URL = "https://www.alphavantage.co/query"

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:
        return "stock_tool"

    @property
    def description(self) -> str:
        return (
            "Fetch real-time stock information "
            "using a stock symbol."
        )

    # ==========================================================
    # Invoke
    # ==========================================================

    def invoke(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Fetch current stock information.

        Parameters
        ----------
        symbol : str
            Stock ticker symbol.

        Returns
        -------
        dict
            Normalized stock data.
        """

        try:

            symbol = symbol.upper().strip()

            logging.info(
                "Fetching stock data for %s",
                symbol,
            )

            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": settings.ALPHA_VANTAGE_API_KEY,
            }

            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=20,
            )

            response.raise_for_status()

            data = response.json()

            # API Limit
            if "Note" in data:
                raise RuntimeError(
                    "Alpha Vantage API rate limit exceeded."
                )

            # API Error
            if "Error Message" in data:
                raise ValueError(
                    data["Error Message"]
                )

            quote = data.get("Global Quote", {})

            if not quote:
                raise ValueError(
                    "Invalid stock symbol."
                )

            result = {

                "symbol":
                    quote.get("01. symbol"),

                "open":
                    float(
                        quote.get(
                            "02. open",
                            0,
                        )
                    ),

                "high":
                    float(
                        quote.get(
                            "03. high",
                            0,
                        )
                    ),

                "low":
                    float(
                        quote.get(
                            "04. low",
                            0,
                        )
                    ),

                "price":
                    float(
                        quote.get(
                            "05. price",
                            0,
                        )
                    ),

                "volume":
                    int(
                        quote.get(
                            "06. volume",
                            0,
                        )
                    ),

                "latest_trading_day":
                    quote.get(
                        "07. latest trading day"
                    ),

                "previous_close":
                    float(
                        quote.get(
                            "08. previous close",
                            0,
                        )
                    ),

                "change":
                    float(
                        quote.get(
                            "09. change",
                            0,
                        )
                    ),

                "change_percent":
                    quote.get(
                        "10. change percent"
                    ),

            }

            logging.info(
                "Stock data fetched successfully."
            )

            return result

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Convenience
    # ==========================================================

    def current_price(
        self,
        symbol: str,
    ) -> dict[str, Any]:

        return self.invoke(symbol)