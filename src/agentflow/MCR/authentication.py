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
        data_source (str): The data source identifier

    Returns:
        Optional[requests.auth.AuthBase]: Authentication object for requests or None
    """
    _logger.debug(f"Generating authentication for {data_source}")

    data_source = "_".join(data_source.upper().split())

    api_key = os.getenv(f"{data_source}_API_KEY", None)

    if data_source == "EVM_API":
        _logger.debug(f"Using {data_source} API key for authentication")
        if not api_key:
            _logger.error(
                f"{data_source}_API_KEY environment variable not set")
            raise ValueError(
                f"{data_source}_API_KEY environment variable not set")
        return APIKeyAuth(api_key)
    else:
        _logger.info(
            f"No API key found for {data_source}, skipping authentication")
        return None
