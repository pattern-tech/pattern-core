
import os
import inspect
import requests

from sqlalchemy import select
from langchain.tools import tool
from sqlalchemy.orm import Session

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


def get_linkedin_posts(query: str, api_key: str) -> dict:
    """
    Search for a query on LinkedIn and process the results.

    Args:
        query (str): The search query string to look up
        api_key (str): The RapidAPI key for authentication

    Returns:
        dict: The raw JSON response from the LinkedIn API
    """
    url = os.getenv("LINKEDIN_SEARCH_URL")

    payload = {
        "keyword": query,
        "sortBy": "date_posted",
    }
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


def get_linkedin_profile(profile_url: str, api_key: str) -> dict:
    """
    Get the profile information for a LinkedIn post.

    Args:
        url (str): The URL of the LinkedIn post
        api_key (str): The RapidAPI key for authentication

    Returns:
        dict: The raw JSON response from the LinkedIn API
    """

    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url"

    querystring = {"url": profile_url}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()


@tool
def get_linkedin_profile_by_url(profile_url: str):
    """
    Get the profile information for a LinkedIn profile by URL.

    Args:
        url (str): The URL of the LinkedIn profile

    Returns:
        dict: The raw JSON response from the LinkedIn API
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting linkedin profile failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    response = get_linkedin_profile(profile_url, api_key_decrypted)

    return response


@ tool
def search_on_linkedin(query):
    """
    Search for posts and content on LinkedIn based on a query.

    Args:
        query (str): The search query string to look up on LinkedIn

    Returns:
        list: A list of dictionaries containing processed LinkedIn posts, where each dictionary has:
            - url (str): The URL of the LinkedIn post
            - content (str): The processed text content of the post
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting linkedin posts failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    response = get_linkedin_posts(query, api_key_decrypted)

    results = []

    for single_response in response['data']['items']:
        text = text_post_process(single_response['text'])
        link = single_response['url']
        results.append({"url": link, "content": text})

    return results
