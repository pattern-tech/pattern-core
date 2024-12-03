import os
import inspect

from sqlalchemy import select
from langchain.tools import tool
from newsapi import NewsApiClient
from sqlalchemy.orm import Session
from src.db.sql_alchemy import Database

from src.db.models import Tool
from src.util.encryption import decrypt_message
from src.shared.error_code import FunctionsErrorCodeEnum

database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fetch_news_by_query(query: str, api_key: str) -> dict:
    """
    Fetches news articles based on a search query using the NewsAPI.

    Args:
        query (str): The search query to find relevant news articles
        api_key (str): API key for authenticating with NewsAPI

    Returns:
        dict: JSON response containing news articles matching the query
              Contains 'articles' list with article details like url, content, etc.
    """

    newsapi = NewsApiClient(api_key=api_key)

    all_articles = newsapi.get_everything(q=query,
                                          language='en',
                                          sort_by='relevancy',
                                          #   sources='bbc-news,the-verge',
                                          #   domains='bbc.co.uk,techcrunch.com',
                                          #   from_param='2024-05-07',
                                          #   to='2024-06-07',
                                          #   page=2
                                          )

    return all_articles


@tool
def get_latest_news(query: str):
    """
    Retrieves the latest news articles based on a search query.

    Args:
        query (str): The search query to find relevant news articles

    Returns:
        list: A list of dictionaries containing news article information
              Each dictionary has 'url' and 'content' (publish date) keys

    Raises:
        None
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

    all_articles = fetch_news_by_query(query, api_key_decrypted)

    results = []

    for news in all_articles['articles']:
        results.append({
            'url': news['url'],
            'content': news['content']
        })

    return results
