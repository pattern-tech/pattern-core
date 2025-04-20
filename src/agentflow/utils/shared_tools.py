import re
import functools
import threading

from functools import wraps
from typing import Any, TypeVar, List, Optional
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from multiprocessing import Process, Queue
from langchain_together import ChatTogether
from langchain_fireworks import ChatFireworks
from langchain.agents import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain.agents import (
    create_openai_functions_agent, create_tool_calling_agent, create_react_agent)

from src.share.logging import Logging
from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType, Prompt
from src.agentflow.llm.llm_wrapper import create_llm_wrapper, LLMWrapper

T = TypeVar('T')

_logger = Logging().get_logger()


class TimeoutException(Exception):
    """Custom exception raised when a function exceeds the specified execution time."""
    pass


def text_post_process(text):
    """
    Post-process text by removing extra whitespace and newlines.

    Args:
        text (str): Input text to be processed

    Returns:
        str: Processed text with normalized whitespace and newlines
    """
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s{2,}', ' ', text)

    return text


def timeout(seconds: int):
    """
    Decorator to enforce a timeout on the execution of the decorated function.

    Args:
        seconds (int): The maximum number of seconds the function is allowed to run.

    Returns:
        callable: The decorated function with timeout enforcement.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that executes the decorated function with timeout enforcement.

            Args:
                *args: Variable length argument list passed to the decorated function.
                **kwargs: Arbitrary keyword arguments passed to the decorated function.

            Returns:
                The result of the decorated function if completed within the timeout period.

            Raises:
                TimeoutException: If the function execution exceeds the specified timeout.
                Exception: If any error occurs during the function execution.
            """
            result_queue = Queue()

            def worker(queue, *args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    queue.put(('result', result))
                except Exception as e:
                    queue.put(('error', e))

            process = Process(target=worker, args=(
                result_queue, *args), kwargs=kwargs)
            process.start()
            process.join(timeout=seconds)

            if process.is_alive():
                process.terminate()
                process.join()
                raise TimeoutException(
                    f'Function timed out after {seconds} seconds')

            if not result_queue.empty():
                status, value = result_queue.get()
                if status == 'error':
                    raise value
                return value

            raise TimeoutException(
                f'Function timed out after {seconds} seconds')

        return wrapper
    return decorator


def time_limit(seconds: int):
    """
    Decorator that attempts to time out a function after 'seconds' using threading.
    This approach is cross-platform, including Windows. However, it cannot
    interrupt certain low-level system or C calls.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # A container to store the result (or exception) from the thread
            result_container = {"result": None, "exception": None}

            def target():
                try:
                    result_container["result"] = func(*args, **kwargs)
                except Exception as e:
                    result_container["exception"] = e

            # Start the function in a separate thread
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(seconds)

            # If the thread is still active, we consider it timed out
            if thread.is_alive():
                # (Optional) attempt to stop the thread politely if you have a cooperative approach
                # Forcibly stopping threads in Python is tricky and not recommended
                raise TimeoutError(
                    f"Function '{func.__name__}' timed out after {seconds} seconds.")

            # If the thread raised an exception, raise it in the main thread
            if result_container["exception"] is not None:
                raise result_container["exception"]

            return result_container["result"]
        return wrapper
    return decorator


def handle_exceptions(func: callable) -> callable:
    """
    Decorator to catch exceptions in the decorated function
    and return the exception message as a string.

    Args:
        func (callable): The function to be decorated

    Returns:
        callable: The wrapped function that handles exceptions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper function that executes the decorated function and handles exceptions.

        Args:
            *args: Variable length argument list passed to the decorated function
            **kwargs: Arbitrary keyword arguments passed to the decorated function

        Returns:
            The result of the decorated function if successful, or an error message string if an exception occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            message = f"Error: {str(e)}, Class: {e.__class__.__name__}"
            _logger.error(message)
            return message
    return wrapper


def init_llm(service: str, model_name: str, api_key: str, stream: bool = False, callbacks: Optional[List[Any]] = None) -> LLMWrapper:
    """
    Initialize an LLM wrapper based on the specified service.

    Args:
        service: The name of the LLM service (e.g., "openai", "anthropic")
        model_name: The name of the model to use
        api_key: API key for authentication
        stream: Whether to stream the response
        callbacks: Optional callbacks for the LLM

    Returns:
        An instance of an LLMWrapper implementation
    """
    return create_llm_wrapper(service, model_name, api_key, stream, callbacks)
