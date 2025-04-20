from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional, Union


class LLMWrapper(ABC):
    """
    Abstract base class for LLM wrappers.
    Provides a standard interface for interacting with various LLM providers.
    """

    @abstractmethod
    def __init__(self, model_name: str, api_key: str, stream: bool = False, callbacks: Optional[List[Any]] = None):
        """
        Initialize the LLM wrapper.

        Args:
            model_name: The name of the model to use
            api_key: API key for authentication
            stream: Whether to stream the response
            callbacks: Optional callbacks for the LLM
        """
        pass

    @abstractmethod
    def invoke(self, messages: List[Tuple[str, str]]) -> Any:
        """
        Send a request to the LLM and get a response.

        Args:
            messages: List of (role, content) tuples representing the conversation

        Returns:
            The LLM response object
        """
        pass


class OpenAIWrapper(LLMWrapper):
    """
    Wrapper for OpenAI's API.
    """

    def __init__(self, model_name: str, api_key: str, stream: bool = False, callbacks: Optional[List[Any]] = None):
        """Initialize the OpenAI wrapper."""
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.stream = stream
        self.callbacks = callbacks

    def invoke(self, messages: List[Tuple[str, str]]) -> Any:
        """Send a request to OpenAI and get a response."""
        # Convert from (role, content) tuples to OpenAI's expected format
        formatted_messages = [
            {"role": "system" if role == "system" else
             "user" if role == "human" else
             "assistant" if role == "ai" else role,
             "content": content}
            for role, content in messages
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted_messages,
            stream=self.stream
        )

        # Create a response object that mimics what other code expects
        if not self.stream:
            class ResponseWrapper:
                def __init__(self, content):
                    self.content = content

            return ResponseWrapper(response.choices[0].message.content)
        return response


class AnthropicWrapper(LLMWrapper):
    """
    Wrapper for Anthropic's API.
    """

    def __init__(self, model_name: str, api_key: str, stream: bool = False, callbacks: Optional[List[Any]] = None):
        """Initialize the Anthropic wrapper."""
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
        self.stream = stream
        self.callbacks = callbacks

    def invoke(self, messages: List[Tuple[str, str]]) -> Any:
        """Send a request to Anthropic and get a response."""
        # Convert from (role, content) tuples to Anthropic's expected format
        formatted_messages = [
            {"role": "assistant" if role == "ai" else
             "user" if role == "human" else
             "user" if role == "system" else role,
             "content": content}
            for role, content in messages
        ]

        response = self.client.messages.create(
            model=self.model_name,
            messages=formatted_messages,
            stream=self.stream
        )

        # Create a response object that mimics what other code expects
        if not self.stream:
            class ResponseWrapper:
                def __init__(self, content):
                    self.content = content

            return ResponseWrapper(response.content[0].text)
        return response


# Factory function to create appropriate wrapper based on service name
def create_llm_wrapper(service: str, model_name: str, api_key: str, stream: bool = False, callbacks: Optional[List[Any]] = None) -> LLMWrapper:
    """
    Factory function to create an LLM wrapper instance.

    Args:
        service: The name of the LLM service (e.g., "openai", "anthropic")
        model_name: The name of the model to use
        api_key: API key for authentication
        stream: Whether to stream the response
        callbacks: Optional callbacks for the LLM

    Returns:
        An instance of an LLMWrapper implementation
    """
    service = service.lower()
    if service == "openai":
        return OpenAIWrapper(model_name, api_key, stream, callbacks)
    elif service in ("anthropic", "claude"):
        return AnthropicWrapper(model_name, api_key, stream, callbacks)
    else:
        raise ValueError(f"Unsupported LLM service: {service}")
