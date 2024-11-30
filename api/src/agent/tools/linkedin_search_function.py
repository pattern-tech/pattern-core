
import os
import requests

from langchain.tools import tool

from src.agent.tools.shared_tools import text_post_process


def get_linkedin_posts(query):
    """
    Search for a query on LinkedIn and process the results.

    Args:
        query (str): The search query string to look up

    Returns:
        list: A list of dictionaries containing processed search results, where each dictionary has:
            - url (str): The source URL of the result
            - content (str): The processed page content
    """
    url = os.getenv("LINKEDIN_SEARCH_URL")

    payload = {
        "keyword": query,
        "sortBy": "date_posted",
    }
    headers = {
        "x-rapidapi-key": os.getenv("LINKEDIN_SEARCH_API_KEY"),
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


@tool
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
    response = get_linkedin_posts(query)

    results = []

    for single_response in response['data']['items']:
        text = text_post_process(single_response['text'])
        link = single_response['url']
        results.append({"url": link, "content": text})

    return results
