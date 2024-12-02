import os
import inspect
import requests

from sqlalchemy import select
from sqlalchemy.orm import Session
from langchain_core.tools import tool

from src.db.models import Tool
from src.db.sql_alchemy import Database
from src.shared.error_code import FunctionsErrorCodeEnum


database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@tool
def get_weather(
    city: str = "London", aqi: str = "no"
) -> dict:
    """
    Fetches the current weather data for a given city using WeatherAPI.

    Args:
        api_key (str): Your WeatherAPI key.
        city (str): The city to fetch weather for. Default is London.
        aqi (str): Whether to include air quality data. Default is "no".

    Returns:
        Optional[WeatherResponse]: The weather data parsed as a Pydantic model or None if an error occurs.
    """

    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    base_url = os.getenv("WEATHER_URL")
    params = {"key": api_key, "q": city, "aqi": aqi}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return f"Get weather service failed. {FunctionsErrorCodeEnum.FAILED.value}"
