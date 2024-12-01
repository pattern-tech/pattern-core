import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from langchain_core.tools import tool

from src.db.models import Tool
from src.shared.error_code import FunctionsErrorCodeEnum


@tool
def get_weather(
    db_session: Session, api_key: str, city: str = "London", aqi: str = "no"
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

    result = db_session.execute(
        select(Tool.api_key).where(Tool.function_name == "get_weather")
    ).scalar_one_or_none()
    if result is None:
        return f"Get weather service failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    base_url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city, "aqi": aqi}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return f"Get weather service failed. {FunctionsErrorCodeEnum.FAILED.value}"
