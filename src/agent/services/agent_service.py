import json
import asyncio
from typing import Dict, Any, AsyncGenerator

from datetime import datetime
from langchain.agents import AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.share.logging import Logging
from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType
from src.agentflow.utils.shared_tools import init_llm, init_agent, init_prompt


class StreamingCallbackHandler(BaseCallbackHandler):
    """
    A callback handler that collects tokens and intermediate events in an asyncio queue.
    Uses a newline-delimited JSON (NDJSON) protocol for reliable streaming.
    Each event is a complete JSON object with a newline terminator.
    Captures detailed information about tool execution including inputs and outputs.
    """

    def __init__(self):
        self.queue = asyncio.Queue()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Handle new tokens from the LLM.

        Args:
            token (str): The new token from the LLM.
            **kwargs: Additional keyword arguments.
        """
        # Create a complete JSON event for each token
        event = {"type": "token", "data": token}
        # Use NDJSON format (newline-delimited JSON)
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_agent_action(self, action, **kwargs) -> None:
        """
        Handle agent actions.

        Args:
            action: The action being performed by the agent.
            **kwargs: Additional keyword arguments.
        """
        event = {
            "type": "agent_start",
            "timestamp": str(datetime.now())
        }
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_agent_finish(self, action, **kwargs) -> None:
        """
        Handle agent finish events.

        Args:
            action: The action being performed by the agent.
            **kwargs: Additional keyword arguments.
        """
        event = {
            "type": "agent_finish",
            "timestamp": str(datetime.now())
        }
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_tool_start(self, serialized, input_str, **kwargs) -> None:
        """
        Handle tool start events.

        Args:
            serialized: The serialized input to the tool.
            input_str: The string representation of the input.
            **kwargs: Additional keyword arguments.
        """
        event = {
            "type": "tool_start",
            "tool_name": serialized["name"],
            "params": input_str,
            "timestamp": str(datetime.now())
        }
        # Use NDJSON format
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_tool_end(self, output, **kwargs) -> None:
        """
        Handle tool completion events.

        Args:
            output: The output produced by the tool.
            **kwargs: Additional keyword arguments.
        """
        # Extract information about the completed tool
        observation = kwargs.get("observation", output)
        tool_name = kwargs.get("name", None)

        # Create a detailed event for tool completion
        event = {
            "type": "tool_end",
            "tool_name": tool_name,
            "output": observation,
            "timestamp": str(datetime.now())
        }
        # Use NDJSON format
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_tool_error(self, error, **kwargs) -> None:
        """
        Handle tool error events.

        Args:
            error: The error that occurred during tool execution.
            **kwargs: Additional keyword arguments.
        """
        # Extract information about the tool that caused the error
        tool_name = kwargs.get("name", None)

        # Create a detailed event for tool error
        event = {
            "type": "tool_error",
            "tool_name": tool_name,
            "error": str(error),
            "timestamp": str(datetime.now())
        }
        # Use NDJSON format
        self.queue.put_nowait(json.dumps(event) + "\n")


class AgentService:
    """
    AgentService is responsible for doing the job
    """

    def __init__(self, tools, MCR, memory=None, streaming: bool = True):
        """
        Initialize the AgentService.

        Args:
            tools: The tools to use for agent
            MCR: Model Context Registry
            memory: The memory to use for storing conversation history
            streaming (bool): Whether to enable streaming responses
        """
        self._logger = Logging().get_logger()
        self._logger.info("Initializing AgentService")

        self.tools = tools
        self.MCR = MCR
        self.memory = memory
        self.streaming = streaming
        self.streaming_handler = None

        # Default timeout values that can be adjusted if needed
        self.token_timeout = 0.2
        self.buffer_timeout = 0.05
        self.poll_interval = 0.1

        # Set up the streaming callback if streaming is enabled.
        if streaming:
            self._logger.debug("Setting up StreamingCallbackHandler")
            self.streaming_handler = StreamingCallbackHandler()

        config = Config.get_config()

        self._logger.info(
            f"Initializing LLM provider: {config['llm']['provider']}, model: {config['llm']['model']}")
        self.llm = init_llm(service=config["llm"]["provider"],
                            model_name=config["llm"]["model"],
                            api_key=config["llm"]["api_key"],
                            stream=streaming,
                            callbacks=[self.streaming_handler] if self.streaming else None)

        self._logger.debug("Initializing agent prompt")
        self.prompt = init_prompt(self.llm, AgentType.MCR_AGENT)

        self._logger.debug("Initializing agent with tools and prompt")
        self.agent = init_agent(self.llm, self.tools, self.prompt)

        if streaming:
            self._logger.debug(
                "Setting up streaming agent executor with callbacks")
            # Wrap each tool with the callback handler to ensure tool events are captured
            wrapped_tools = []
            for tool in self.tools:
                # Create a copy of the tool with callbacks attached
                tool_with_callbacks = tool.copy()
                tool_with_callbacks.callbacks = [self.streaming_handler]
                wrapped_tools.append(tool_with_callbacks)

            # Make sure the streaming handler is registered for all events, including tool completion
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=wrapped_tools,  # Use the wrapped tools with callbacks
                return_intermediate_steps=True,
                verbose=True,
                callbacks=[self.streaming_handler],
                max_iterations=20,
                max_execution_time=60*3,  # second
                handle_tool_error=True  # Ensure tool errors are also captured
            )
        else:
            self._logger.debug("Setting up non-streaming agent executor")
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                max_iterations=20,
                max_execution_time=60*3,  # second
                return_intermediate_steps=True,
                verbose=True
            )

        if self.memory:
            self._logger.debug("Setting up agent with conversation history")
            self.agent_with_chat_history = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

    async def _process_complete_json(self, buffer: str) -> tuple[list[str], str]:
        """
        Process a buffer to extract complete JSON objects.

        Args:
            buffer (str): The buffer containing JSON data.

        Returns:
            tuple: A tuple containing a list of complete JSON strings and any remaining buffer.
        """
        results = []
        remaining = buffer

        # Process all complete objects in the buffer
        while "\n" in remaining:
            json_str, remaining = remaining.split("\n", 1)
            if json_str:  # Only include non-empty strings
                results.append(json_str + "\n")

        return results, remaining

    async def stream(self, message: str) -> AsyncGenerator[str, None]:
        """
        Stream the agent's response to the input message.

        Args:
            message (str): The input message to be processed by the agent.

        Yields:
            str: Tokens of the agent's response as they become available.

        Raises:
            asyncio.TimeoutError: If waiting for a token from the queue times out.

        Notes:
            This method uses an efficient NDJSON streaming protocol for reliable parsing.
            It supports both memory and non-memory modes, adapting the execution method accordingly.
            Includes a heartbeat mechanism to keep the connection alive during long processing.
        """
        self._logger.info("Starting streaming response to message")
        self._logger.debug(f"Message: {message[:50]}..." if len(
            message) > 50 else f"Message: {message}")

        if not self.streaming or not self.streaming_handler:
            error_msg = "Streaming is not enabled"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        # Clear any leftover tokens
        while not self.streaming_handler.queue.empty():
            self.streaming_handler.queue.get_nowait()
        self._logger.debug("Cleared existing tokens from queue")

        # Send an initial heartbeat message to inform the client that processing has started
        init_heartbeat_event = {
            "type": "heartbeat",
            "data": "processing_started"
        }
        self._logger.debug("Sending initial heartbeat event")
        yield json.dumps(init_heartbeat_event) + "\n"

        # Start the agent task based on memory configuration
        if self.memory:
            self._logger.debug("Using memory-based agent execution")
            loop = asyncio.get_running_loop()
            task = loop.run_in_executor(
                None,
                lambda: self.agent_with_chat_history.invoke(
                    input={"input": message, "MCR": self.MCR},
                    config={"configurable": {"session_id": "ـ"}}
                )
            )
        else:
            self._logger.debug("Using non-memory agent execution")
            task = asyncio.create_task(
                self.agent_executor.arun({"input": message, "MCR": self.MCR})
            )

        buffer = ""  # Initialize an empty buffer for accumulating incomplete JSON
        last_activity = asyncio.get_event_loop().time()  # Track the last activity time
        heartbeat_interval = 15.0  # Send heartbeat every 15 seconds
        total_tokens_processed = 0

        # Continue processing while the task is running or queue has items
        self._logger.debug("Starting token processing loop")
        while not task.done() or not self.streaming_handler.queue.empty():
            try:
                # Try to get a token with a timeout to maintain responsiveness
                token = await asyncio.wait_for(
                    self.streaming_handler.queue.get(),
                    timeout=self.token_timeout
                )

                total_tokens_processed += 1
                if total_tokens_processed % 100 == 0:
                    self._logger.debug(
                        f"Processed {total_tokens_processed} tokens so far")

                # Update the last activity time when we receive a token
                last_activity = asyncio.get_event_loop().time()

                # Add the new token to our buffer
                buffer += token

                # If we have complete JSON objects (ending with newline), process them
                if "\n" in buffer:
                    complete_jsons, buffer = await self._process_complete_json(buffer)
                    for json_str in complete_jsons:
                        yield json_str

            except asyncio.TimeoutError:
                # No new tokens available, check if we should send a heartbeat
                current_time = asyncio.get_event_loop().time()
                if current_time - last_activity >= heartbeat_interval:
                    # Send a heartbeat to keep the connection alive
                    heartbeat_event = {
                        "type": "heartbeat",
                        "data": "still_processing"
                    }
                    self._logger.debug(
                        "Sending heartbeat event due to inactivity")
                    yield json.dumps(heartbeat_event) + "\n"
                    last_activity = current_time  # Reset the activity timer

                # Wait a bit before checking again
                await asyncio.sleep(self.poll_interval)
                continue
            except asyncio.CancelledError:
                # Handle task cancellation gracefully
                self._logger.warning("Stream was cancelled")
                error_event = {
                    "type": "info",
                    "data": "Stream was cancelled"
                }
                yield json.dumps(error_event) + "\n"
                break
            except ConnectionError as e:
                # Handle connection errors specifically
                self._logger.error(
                    f"Connection error during streaming: {str(e)}")
                error_event = {
                    "type": "error",
                    "data": f"Connection error: {str(e)}"
                }
                yield json.dumps(error_event) + "\n"
                break
            except Exception as e:
                # Handle any parsing or processing errors
                self._logger.error(
                    f"Error during streaming: {str(e)}", exc_info=True)
                error_event = {
                    "type": "error",
                    "data": f"Streaming error: {str(e)}"
                }
                yield json.dumps(error_event) + "\n"
                # Continue processing despite errors

        self._logger.info(
            f"Streaming completed. Processed {total_tokens_processed} tokens.")
        # If there's anything left in the buffer after task completion, process it
        if buffer:
            try:
                # Try to parse it as JSON and yield if valid
                json.loads(buffer)  # This is just a validation check
                yield buffer if buffer.endswith("\n") else buffer + "\n"
            except json.JSONDecodeError:
                # If it's not valid JSON, wrap it in an error event
                self._logger.warning(f"Invalid JSON in final buffer: {buffer}")
                error_event = {
                    "type": "error",
                    "data": f"Invalid JSON in final buffer: {buffer}"
                }
                yield json.dumps(error_event) + "\n"

    def ask(self, message: str) -> Dict[str, Any]:
        """
        Sends a message to the agent and returns the response.

        Args:
            message (str): The message to send to the agent.

        Returns:
            Dict[str, Any]: The response from the agent.
        """
        self._logger.info("Processing non-streaming request")
        self._logger.debug(f"Message: {message[:50]}..." if len(
            message) > 50 else f"Message: {message}")

        try:
            if self.memory:
                self._logger.debug("Using memory-based agent execution")
                response = self.agent_with_chat_history.invoke(
                    input={"input": message, "MCR": self.MCR},
                    config={"configurable": {"session_id": "ـ"}}
                )
            else:
                self._logger.debug("Using non-memory agent execution")
                response = self.agent_executor.invoke(
                    {"input": message, "MCR": self.MCR})

            output_length = len(response.get("output", ""))
            steps_count = len(response.get("intermediate_steps", []))
            self._logger.info(
                f"Request completed successfully. Output length: {output_length}, Steps: {steps_count}")

            # Log each tool use
            for idx, step in enumerate(response.get("intermediate_steps", [])):
                self._logger.info(f"Tool execution {idx+1}: {step[0].tool}")

            return response

        except Exception as e:
            self._logger.error(
                f"Error during agent request: {str(e)}", exc_info=True)
            raise
