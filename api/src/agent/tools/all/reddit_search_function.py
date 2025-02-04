
import os
import inspect
import requests

from sqlalchemy import select
from langchain.tools import tool

from src.db.models import Tool
from src.db.sql_alchemy import Database
from src.util.encryption import decrypt_message
from src.shared.error_code import FunctionsErrorCodeEnum
from src.agent.tools.shared_tools import text_post_process

database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_reddit_posts(query: str, api_key: str) -> dict:
    """
    Makes an API request to Reddit search endpoint to fetch posts matching a query.

    Args:
        query (str): The search query string to look up on Reddit

    Returns:
        dict: JSON response containing Reddit posts data matching the query
    """

    url = os.getenv("REDDIT_SEARCH_URL")

    querystring = {"query": query,
                   "sort": "RELEVANCE",
                   "time": "all",
                   "nsfw": "0"}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "reddit-scraper2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()


@tool
def search_on_reddit(query):
    """
    Search for latest trends and posts on Reddit based on a query.

    Args:
        query (str): The search query string to look up on Reddit

    Returns:
        str: Processed text content combined from all matching Reddit posts
    """

    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting latest news failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    response = get_reddit_posts(query, api_key_decrypted)

    result = []

    for single_response in response['data']:
        text = text_post_process(single_response['content']['text'])
        link = single_response['url']
        result.append({"url": link, "content": text})

    return result
