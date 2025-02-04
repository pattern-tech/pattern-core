import re

from typing import TypeVar
from functools import wraps
from multiprocessing import Process, Queue

T = TypeVar('T')


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


def timeout(seconds):
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
            return f"Error: {str(e)}, Class: {e.__class__.__name__}"
    return wrapper
