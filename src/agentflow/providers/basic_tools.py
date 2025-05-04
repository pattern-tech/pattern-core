import time
import dateparser

from langchain.tools import tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@tool
def get_current_timestamp() -> int:
    """
    Get the current Unix timestamp.

    Returns:
        int: The current timestamp.
    """
    return int(time.time())


@tool
def convert_to_timestamp(date_str: str) -> int:
    """
    Convert a natural language date string into a Unix timestamp.

    Args:
        date_str (str): A human-readable date (e.g., "one month ago", "12/3/2020").

    Returns:
        int: The Unix timestamp corresponding to the provided date.

    Raises:
        ValueError: If the date string cannot be parsed.
    """
    parsed_date = dateparser.parse(date_str)
    if parsed_date:
        return int(time.mktime(parsed_date.timetuple()))
    else:
        raise ValueError(f"Could not parse the date string: {date_str}")
