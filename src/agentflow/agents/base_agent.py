import json
from typing import List, Dict, Any, Callable, Optional, Set, TypedDict, Union
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import ChatCompletionMessage


class ToolCall(TypedDict):
    """Type definition for a tool call."""
    function_name: str
    args: Dict[str, Any]


class ResponseDict(TypedDict):
    """Type definition for the response dictionary."""
    response: Union[str, ChatCompletionMessage]
    tool_calls: List[ToolCall]


class ChatResult(TypedDict):
    """Type definition for the chat result."""
    intermediate_steps: List[ToolCall]
    iterations_used: int
    final_response: str


class OraAgent:
    """
    An agent that leverages the ORA API for function calling capabilities.

    This agent provides an interface to interact with ORA's API, allowing for:
    - Registration of custom tools/functions
    - Conversation management with history tracking
    - Automatic function calling based on LLM decisions
    - Deduplication of repeated function calls
    """

    def __init__(
        self,
        api_key: str,
        model: str = "meta-llama/Llama-3.3-70B-Instruct",
        system_content: str = "You are an expert Ethereum blockchain assistant"
            "- Break the user task into sequential sub tasks (if needed) and execute them step by step"
            "- If you can not do the task with the tools you have say 'I am unable to process this task'"
            "- You have access to tools to answer user queries. Use tools when appropriate."
            "- end the conversation by saying ONLY `END_OF_CONVERSATION`."
            "- If you got the result of requested tool, you should end the conversation."
    ) -> None:
        """
        Initialize the ORA agent with API credentials and configuration.

        Args:
            api_key: ORA API key for authentication
            model: Model identifier to use for chat completions
            system_content: System prompt that defines the assistant's behavior and capabilities
        """
        self.api_key: str = api_key
        self.model: str = model
        self.system_content: str = system_content
        self.client: OpenAI = OpenAI(
            api_key=api_key,
            base_url="https://api.ora.io/v1/",
        )
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize system message if provided
        if system_content:
            self.conversation_history.append(
                {"role": "system", "content": system_content})

        # Dictionary mapping function names to their implementations
        self.available_functions: Dict[str, Callable] = {}

        # List of tool definitions in OpenAI format
        self.tools: List[Dict[str, Any]] = []

    def add_tool(self, tool_definition: Dict[str, Any], function_impl: Callable) -> None:
        """
        Register a tool with the agent for use in conversations.

        This method adds a tool definition to the agent's available tools and maps
        the function name to its implementation for execution when called.

        Args:
            tool_definition: OpenAI-compatible tool definition containing name, 
                             description, and parameters schema
            function_impl: The actual function implementation to call when the 
                           tool is invoked by the model
        """
        # Extract and append the Returns section from docstring to the tool description
        returns_section = self._extract_returns_section(
            function_impl.__doc__ or "")
        if returns_section:
            tool_definition["function"]["description"] += f"\n{returns_section}"

        # Register the tool and its implementation
        self.tools.append(tool_definition)
        self.available_functions[tool_definition["function"]
                                 ["name"]] = function_impl

    def _get_messages(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history formatted for the API.

        Returns:
            List of message dictionaries in the format expected by the OpenAI API
        """
        return self.conversation_history

    def _handle_response(self, response: ChatCompletion) -> ResponseDict:
        """
        Process tool calls returned by the model and execute the corresponding functions.

        This method extracts tool calls from the model's response, executes the
        associated functions with the provided arguments, and formats the results.

        Args:
            response: The response object from the OpenAI chat completion API

        Returns:
            Dictionary containing the processed response and any tool call information
        """
        message = response.choices[0].message
        final_response: ResponseDict = {"response": message, "tool_calls": []}

        # Handle tool calls if present
        if message.tool_calls:
            response_text = ""
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute function if it exists in our registry
                if function_name in self.available_functions:
                    tool_call_info: ToolCall = {
                        "function_name": function_name,
                        "args": function_args
                    }
                    final_response["tool_calls"].append(tool_call_info)

                    # Call the function and append its result to the response
                    function_result = self.available_functions[function_name](
                        **function_args)
                    response_text += str(function_result) + "\n"
        else:
            # Use the message content if no tool calls
            response_text = message.content or ""

        final_response["response"] = response_text
        return final_response

    def _extract_returns_section(self, text: str) -> str:
        """
        Extract the Returns section from a function's docstring.

        Args:
            text: The docstring text to parse

        Returns:
            The extracted Returns section or an empty string if not found
        """
        if not text:
            return ""

        keyword = "Returns:"
        start_index = text.find(keyword)
        if start_index == -1:
            return ""
        return text[start_index:].strip()

    def _check_end_of_conversation(self, response: ResponseDict) -> bool:
        """
        Determine if the conversation has reached its conclusion.

        This method checks if the conversation should continue based on:
        1. Presence of tool calls that need to be processed
        2. Explicit end-of-conversation marker in the response

        Args:
            response: The processed response dictionary from _handle_response

        Returns:
            True if the conversation should continue, False if it should end
        """
        # Continue if there are tool calls to process
        if response.get("tool_calls"):
            return True

        # Check for explicit end marker
        response_text = response.get("response", "")
        if isinstance(response_text, str) and "END_OF_CONVERSATION" in response_text:
            return False

        # End the conversation if we have a complete response with no tool calls
        return False

    def chat(self, user_input: str, max_iterations: int = 5) -> ChatResult:
        """
        Process a user input, executing all necessary tools until completion.

        This method implements a conversation loop that:
        1. Sends the user query to the model
        2. Identifies any tools the model wants to call
        3. Executes those tools and adds results to the conversation
        4. Repeats until no more tool calls are needed or max iterations reached
        5. Generates a final response synthesizing all function results

        The method also handles deduplication of function calls to prevent
        redundant executions of the same function with the same arguments.

        Args:
            user_input: The user's message or query
            max_iterations: Maximum number of model-tool interaction cycles allowed
                           (prevents infinite loops)

        Returns:
            Dictionary containing the final response, intermediate steps,
            and number of iterations used
        """
        # Add user input to conversation history
        self.conversation_history.append(
            {"role": "user", "content": user_input})

        intermediate_steps: List[ToolCall] = []
        iteration: int = 0
        should_continue: bool = True
        final_response: str = ""

        # Track function calls to avoid duplicates using a set of unique keys
        called_functions: Set[str] = set()

        # Main conversation loop
        while should_continue and iteration < max_iterations:
            iteration += 1

            # Create chat completion with the current conversation and tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._get_messages(),
                tools=self.tools if self.tools else None
            )

            # Process the response and extract tool calls
            result = self._handle_response(response)

            # Check if we need to continue the conversation
            should_continue = self._check_end_of_conversation(result)

            # Process tool calls with deduplication
            if result["tool_calls"]:
                new_tool_calls: List[ToolCall] = []

                for tool_call in result["tool_calls"]:
                    # Create a unique key for this function call
                    func_key = f"{tool_call['function_name']}:{json.dumps(tool_call['args'], sort_keys=True)}"

                    # Only process new, unique function calls
                    if func_key not in called_functions:
                        called_functions.add(func_key)
                        new_tool_calls.append(tool_call)

                # Track all unique tool calls
                intermediate_steps.extend(new_tool_calls)

                # End if we've processed all unique tool calls
                if not new_tool_calls:
                    should_continue = False

            # Update the final response
            final_response = result["response"] if isinstance(
                result["response"], str) else ""

            # Add the assistant's response to conversation history when finished
            if not should_continue or iteration == max_iterations:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })

        # Return the final result with all intermediate steps
        return {
            "intermediate_steps": intermediate_steps,
            "iterations_used": iteration,
            "final_response": final_response
        }

    def reset_conversation(self) -> None:
        """
        Reset the conversation history, preserving only the system message if present.

        This method clears the conversation history but maintains the system prompt,
        allowing for a fresh conversation with the same agent configuration.
        """
        if self.system_content:
            self.conversation_history = [
                {"role": "system", "content": self.system_content}
            ]
        else:
            self.conversation_history = []
