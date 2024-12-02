import os
import json
import inspect
import requests

from sqlalchemy import select
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.document_loaders import WebBaseLoader

from src.db.models import Tool
from src.db.sql_alchemy import Database
from src.shared.error_code import FunctionsErrorCodeEnum
from src.agent.tools.shared_tools import text_post_process

database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def search_on_google(query: str, api_key: str) -> dict:
    """
    Search for a query using the Google Serper API.

    Args:
        query (str): The search query string to look up
        api_key (str): API key for authentication with Google Serper API

    Returns:
        dict: A dictionary of search results from Google, containing information like titles,
             snippets and links for each result
    """

    url = os.getenv("GOOGLE_SEARCH_URL")

    payload = json.dumps({
        "q": query
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)["organic"]


@tool
def search_on_web_by_query(query: str) -> list:
    """
    Search for a query on the web using Google and process the results.

    Args:
        query (str): The search query string to look up

    Returns:
        list: A list of dictionaries containing processed search results, where each dictionary has:
            - url (str): The source URL of the result
            - content (str): The processed page content
    """
    results = []

    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    search_results = search_on_google(query, api_key)

    links = [res['link'] for res in search_results]

    docs = [WebBaseLoader(link).load() for link in links[:5]]
    docs_list = [item for sublist in docs for item in sublist]

    for doc in docs_list:
        doc.page_content = text_post_process(doc.page_content)

    results = [{'url': doc.metadata['source'], 'content': doc.page_content}
               for doc in docs_list]

    return results
