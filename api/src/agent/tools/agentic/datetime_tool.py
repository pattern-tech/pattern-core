from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_datetime():
    """
    Get the current date and time.

    Returns:
        datetime: Current date and time as a datetime object
    """
    return datetime.now()
