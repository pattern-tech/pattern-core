from langchain_core.tools import tool


@tool
def add(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a (float): First number
        b (float): Second number

    Returns:
        float: Sum of the two numbers
    """
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers together.

    Args:
        a (float): First number
        b (float): Second number

    Returns:
        float: Product of the two numbers
    """
    return a * b
