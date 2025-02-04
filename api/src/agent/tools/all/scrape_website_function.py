import os
import requests

from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.document_loaders import WebBaseLoader

from src.agent.tools.shared_tools import text_post_process


@tool
def get_content_of_website(url: str) -> str:
    """
    Load and process the content of a given website URL.

    Args:
        url (str): The URL of the website to load and process

    Returns:
        dict: A dictionary containing the processed website content with:
            - url (str): The source URL of the website
            - content (str): The processed text content of the website
    """

    doc = WebBaseLoader(url).load()[0]

    doc.page_content = text_post_process(doc.page_content)

    result = {'url': doc.metadata['source'], 'content': doc.page_content}

    return result
