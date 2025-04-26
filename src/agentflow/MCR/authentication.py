import os
import requests

from typing import Optional

from src.share.logging import Logging


# Initialize logger
_logger = Logging().get_logger()

class APIKeyAuth(requests.auth.AuthBase):
    """
    Authentication handler for API key based authentication.
    Implements the requests.auth.AuthBase interface.
    """

    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["X-API-Key"] = self.api_key
        return r


def authenticate(data_source: str) -> Optional[requests.auth.AuthBase]:
    """
    Provides authentication for a specific data source.

    Args:
        data_source (str): The data source identifier (e.g., "MORALIS")

    Returns:
        Optional[requests.auth.AuthBase]: Authentication object for requests or None
    """
    _logger.debug(f"Generating authentication for {data_source}")
    if data_source == "MORALIS":
        api_key = os.getenv("MORALIS_API_KEY")
        if not api_key:
            _logger.error("MORALIS_API_KEY environment variable not set")
            raise ValueError("MORALIS_API_KEY environment variable not set")

        return APIKeyAuth(api_key)
    return None
