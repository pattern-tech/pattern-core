
import os
import requests

from langchain.tools import tool

from src.agent.tools.shared_tools import text_post_process


def get_reddit_posts(query):
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
        "x-rapidapi-key": os.getenv("REDDIT_SEARCH_API_KEY"),
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

    response = get_reddit_posts(query)

    result = []

    for single_response in response['data']:
        text = text_post_process(single_response['content']['text'])
        link = single_response['url']
        result.append({"url": link, "content": text})

    return result
