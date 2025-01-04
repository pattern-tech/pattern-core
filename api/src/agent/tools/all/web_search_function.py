from langchain.tools import tool
import os
import json
import inspect
import requests

from sqlalchemy import select
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.document_loaders import WebBaseLoader

from src.db.models import Tool
from src.db.sql_alchemy import Database
from src.util.encryption import decrypt_message
from src.shared.error_code import FunctionsErrorCodeEnum
from src.agent.tools.shared_tools import text_post_process
from src.agent.tools.shared_tools import handle_exceptions, timeout

database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# updated to Tavily and Perplexity
'''
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

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    search_results = search_on_google(query, api_key_decrypted)

    links = [res['link'] for res in search_results]

    docs = [WebBaseLoader(link).load() for link in links[:5]]
    docs_list = [item for sublist in docs for item in sublist]

    for doc in docs_list:
        doc.page_content = text_post_process(doc.page_content)

    results = [{'url': doc.metadata['source'], 'content': doc.page_content}
               for doc in docs_list]

    return results
'''


@tool
@handle_exceptions
# @timeout(seconds=10)
def web_search_tavily(query: str, include_domains: list[str] = [], max_results: int = 5) -> list[dict]:
    """
    Searches the web using the Tavily API for a given query.
    Note: The results is the most updated version.

    Args:
        query (str): The search query string.
        include_domains (list[str], optional): A list of domains to include in the search. Defaults to an empty list.
        max_results (int, optional): Maximum number of results to return. Defaults to 5.

    Returns:
        list[dict]: A list of search result dictionaries.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('TAVILY_URL')}/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "api_key": api_key_decrypted,
        "include_domains": include_domains
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["results"]


@tool
@handle_exceptions
# @timeout(seconds=10)
def get_content_of_websites(links: list[str]) -> list[dict]:
    """
    Extracts content from a list of website URLs using the Tavily API.

    Args:
        links (list[str]): A list of website URLs to extract content from.

    Returns:
        list[dict]: A list of dictionaries containing the extracted content from each URL.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('TAVILY_URL')}/extract"
    headers = {"Content-Type": "application/json"}
    data = {
        "urls": links,
        "api_key": api_key_decrypted,
    }

    response = requests.post(url, headers=headers, json=data)

    final_result = []
    for result in response.json()["results"]:
        final_result.append({
            "url": result["url"],
            "raw_content": text_post_process(result["raw_content"])
        })
    return final_result


@tool
@handle_exceptions
# @timeout(seconds=10)
def web_search_perplexity(query: str, include_domains: list[str] = []) -> str:
    """
    Searches the web using the Perplexity API for a given query and returns the content with citations.
    Note: The results is the most updated version.

    Args:
        query (str): The search query.
        include_domains (list[str], optional): A list of domains to include in the search filter. Defaults to an empty list.

    Returns:
        str: The content of the response from the API with appended citations, or an error message if the request fails.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('PERPLEXITY_URL')}/chat/completions"
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": f"{query}"
            }
        ],
        "search_domain_filter": include_domains,
    }
    headers = {
        "Authorization": f"Bearer {api_key_decrypted}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        res = response.json()
        return res['choices'][0]['message']['content'] + "\n\ncitations\n--------\n" + "\n".join(res['citations'])
    else:
        return "Request failed"


@tool
@handle_exceptions
# @timeout(seconds=10)
def web_search_exa(query: str, include_domains: list[str] = [], num_results: int = 5) -> dict:
    """
    Search the web with an Exa prompt-engineered query. Returns a list of links relevant to the query.
    Note: The results may not be the most updated version

    Args:
        query (str): The search query string.
        num_results (int): The number of results to return. Default is 5.

    Returns:
        dict: A dictionary containing the search results from the API.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('EXA_URL')}/search"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-api-key': api_key_decrypted
    }
    data = {
        "query": query,
        "type": "auto",
        "useAutoprompt": True,
        "includeDomains": include_domains,
        "numResults": num_results,
        "contents": {
            "text": True
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["results"]


@tool
@handle_exceptions
# @timeout(seconds=10)
def get_content_of_exa_document(content_ids: list[str]) -> str:
    """
    Retrieve contents of documents based on a list of document IDs.

    Args:
        content_ids (list[str]): A list of content IDs for which to retrieve the document content.

    Returns:
        str: A string containing the concatenated content of the requested documents.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('EXA_URL')}/contents"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-api-key': api_key_decrypted
    }
    data = {
        "ids": content_ids,
        "contents": {
            "text": True
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["results"]


@tool
@handle_exceptions
# @timeout(seconds=10)
def find_similar_links(link: str, num_results: int = 5) -> list:
    """
    Searches the Exa API to find links similar to the provided link.

    Args:
        link (str): The URL for which similar links are to be found.
        num_results (int): The number of similar links to return. Default is 5.

    Returns:
        list: A list of similar links obtained from the API.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"searching in web failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('EXA_URL')}/findSimilar"

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-api-key': api_key_decrypted
    }
    data = {
        "url": link,
        "numResults": num_results,
        "contents": {
            "text": True
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()["results"]
