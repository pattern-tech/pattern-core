import re

from typing import TypeVar
from functools import wraps
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from multiprocessing import Process, Queue
from langchain_together import ChatTogether
from langchain_fireworks import ChatFireworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

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


def init_llm(service: str, model_name: str, api_key: str, stream: bool = False, callbacks=None):
    """
    Returns an instance of a language model based on the specified service.

    Args:
        service (str): The name of the service to use (e.g., "openai", "groq", "fireworks",
            "together", "huggingface", "ollama").
        model_name (str): The name of the model to use.
        api_key (str): The API key for the specified service.
        stream (bool, optional): Whether to enable streaming for the model. Defaults to False.
        callbacks (StreamingCallbackHandler, optional): callback functions for the model. Defaults to None.

    Returns:
        An instance of the specified language model.

    Raises:
        NotImplementedError: If the specified service is not supported.
    """
    if service == "openai":
        return ChatOpenAI(
            model=model_name,
            streaming=False,
            api_key=api_key,
            callbacks=callbacks
        )
    elif service == "google":
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            streaming=stream,
            callbacks=callbacks
        )
    elif service == "groq":
        return ChatGroq(
            model=model_name,
            api_key=api_key,
            streaming=stream,
            callbacks=callbacks
        )
    elif service == "fireworks":
        return ChatFireworks(
            model=model_name,
            api_key=api_key,
            streaming=stream,
            callbacks=callbacks
        )
    elif service == "together":
        return ChatTogether(
            model=model_name,
            together_api_key=api_key,
            streaming=stream,
            callbacks=callbacks
        )
    elif service == "huggingface":
        pipeline_kwargs = {
            "max_new_tokens": 512,
            "do_sample": False,
            "repetition_penalty": 1.03,
        }
        model = HuggingFacePipeline.from_model_id(
            model_id=model_name,
            task="text-generation",
            pipeline_kwargs=pipeline_kwargs,
            device_map="cpu"
        )
        return ChatHuggingFace(llm=model, callbacks=callbacks)
    elif service == "ollama":
        return ChatOllama(
            model=model_name,
            streaming=stream,
            callbacks=callbacks
        )
    else:
        raise NotImplementedError(f"Service {service} is not supported.")
