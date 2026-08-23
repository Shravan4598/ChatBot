"""
tools/weather_tool.py

Production Weather Tool.

Responsibilities
----------------
- Fetch current weather
- Return normalized weather data
- Handle API failures gracefully
"""

from __future__ import annotations

from typing import Any

import requests

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging

from tools.base_tool import BaseTool


class WeatherTool(BaseTool):
    """
    Current Weather Tool.
    """

    BASE_URL = "http://api.weatherstack.com/current"

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def name(self) -> str:

        return "weather_tool"

    @property
    def description(self) -> str:

        return (
            "Get current weather information "
            "for any city."
        )

    # ==========================================================
    # Invoke
    # ==========================================================

    def invoke(
        self,
        city: str,
    ) -> dict[str, Any]:

        try:

            logging.info(
                "Fetching weather for %s",
                city,
            )

            params = {

                "access_key":
                    settings.WEATHER_API_KEY,

                "query":
                    city,

            }

            response = requests.get(

                self.BASE_URL,

                params=params,

                timeout=20,

            )

            response.raise_for_status()

            data = response.json()

            if data.get("success") is False:

                raise ValueError(

                    data.get(
                        "error",
                        {},
                    ).get(
                        "info",
                        "Weather API Error",
                    )

                )

            location = data.get(
                "location",
                {},
            )

            current = data.get(
                "current",
                {},
            )

            weather = {

                "city":
                    location.get("name"),

                "country":
                    location.get("country"),

                "region":
                    location.get("region"),

                "local_time":
                    location.get("localtime"),

                "temperature":
                    current.get("temperature"),

                "feels_like":
                    current.get("feelslike"),

                "humidity":
                    current.get("humidity"),

                "wind_speed":
                    current.get("wind_speed"),

                "wind_degree":
                    current.get("wind_degree"),

                "wind_direction":
                    current.get("wind_dir"),

                "pressure":
                    current.get("pressure"),

                "visibility":
                    current.get("visibility"),

                "uv_index":
                    current.get("uv_index"),

                "condition":

                    current.get(
                        "weather_descriptions",
                        [],
                    ),

            }

            logging.info(
                "Weather fetched successfully."
            )

            return weather

        except Exception as e:

            raise ChatBotException(e)

    # ==========================================================
    # Convenience
    # ==========================================================

    def current_weather(
        self,
        city: str,
    ) -> dict[str, Any]:

        return self.invoke(city)