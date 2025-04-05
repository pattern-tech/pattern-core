import json
import asyncio
from typing import Dict, Any, AsyncGenerator

from langchain.agents import AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType
from src.agentflow.utils.shared_tools import init_llm, init_agent, init_prompt


class StreamingCallbackHandler(BaseCallbackHandler):
    """
    A callback handler that collects tokens and intermediate events in an asyncio queue.
    Uses a newline-delimited JSON (NDJSON) protocol for reliable streaming.
    Each event is a complete JSON object with a newline terminator.
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
            "type": "tool_start",
            "tool": getattr(action, "tool", None),
            "tool_input": getattr(action, "tool_input", {})
        }
        # Use NDJSON format
        self.queue.put_nowait(json.dumps(event) + "\n")


class RouterAgentService:
    """
    RouterAgentService is responsible for routing the input message to the appropriate agent
    and returning the response.
    """

    def __init__(self, sub_agents, memory=None, streaming: bool = True):
        """
        Initialize the RouterAgentService.

        Args:
            sub_agents: The sub-agents to use for routing.
            memory: The memory to use for storing conversation history.
            streaming (bool): Whether to enable streaming responses.
        """
        self.sub_agents = sub_agents
        self.memory = memory
        self.streaming = streaming
        self.streaming_handler = None

        # Default timeout values that can be adjusted if needed
        self.token_timeout = 0.5  # Increased from 0.01
        self.buffer_timeout = 0.1  # Increased from 0.005
        self.poll_interval = 0.1  # Increased from 0.01

        # Set up the streaming callback if streaming is enabled.
        if streaming:
            self.streaming_handler = StreamingCallbackHandler()

        config = Config.get_config()

        self.llm = init_llm(service=config["llm"]["provider"],
                            model_name=config["llm"]["model"],
                            api_key=config["llm"]["api_key"],
                            stream=streaming,
                            callbacks=[self.streaming_handler] if self.streaming else None)

        self.prompt = init_prompt(self.llm, AgentType.ROUTER_AGENT)

        self.agent = init_agent(self.llm, self.sub_agents, self.prompt)

        if streaming:
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.sub_agents,
                return_intermediate_steps=True,
                verbose=True,
                callbacks=[self.streaming_handler]
            )
        else:
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.sub_agents,
                return_intermediate_steps=True,
                verbose=True
            )

        if self.memory:
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
        if not self.streaming or not self.streaming_handler:
            raise ValueError("Streaming is not enabled")

        # Clear any leftover tokens
        while not self.streaming_handler.queue.empty():
            self.streaming_handler.queue.get_nowait()

        # Start the agent task based on memory configuration
        if self.memory:
            loop = asyncio.get_running_loop()
            task = loop.run_in_executor(
                None,
                lambda: self.agent_with_chat_history.invoke(
                    input={"input": message},
                    config={"configurable": {"session_id": "ـ"}}
                )
            )
        else:
            task = asyncio.create_task(
                self.agent_executor.arun({"input": message})
            )

        buffer = ""  # Initialize an empty buffer for accumulating incomplete JSON
        last_activity = asyncio.get_event_loop().time()  # Track the last activity time
        heartbeat_interval = 15.0  # Send heartbeat every 15 seconds

        # Continue processing while the task is running or queue has items
        while not task.done() or not self.streaming_handler.queue.empty():
            try:
                # Try to get a token with a timeout to maintain responsiveness
                token = await asyncio.wait_for(
                    self.streaming_handler.queue.get(),
                    timeout=self.token_timeout
                )

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
                    yield json.dumps(heartbeat_event) + "\n"
                    last_activity = current_time  # Reset the activity timer

                # Wait a bit before checking again
                await asyncio.sleep(self.poll_interval)
                continue
            except asyncio.CancelledError:
                # Handle task cancellation gracefully
                error_event = {
                    "type": "info",
                    "data": "Stream was cancelled"
                }
                yield json.dumps(error_event) + "\n"
                break
            except ConnectionError as e:
                # Handle connection errors specifically
                error_event = {
                    "type": "error",
                    "data": f"Connection error: {str(e)}"
                }
                yield json.dumps(error_event) + "\n"
                break
            except Exception as e:
                # Handle any parsing or processing errors
                error_event = {
                    "type": "error",
                    "data": f"Streaming error: {str(e)}"
                }
                yield json.dumps(error_event) + "\n"
                # Continue processing despite errors

        # If there's anything left in the buffer after task completion, process it
        if buffer:
            try:
                # Try to parse it as JSON and yield if valid
                json.loads(buffer)  # This is just a validation check
                yield buffer if buffer.endswith("\n") else buffer + "\n"
            except json.JSONDecodeError:
                # If it's not valid JSON, wrap it in an error event
                error_event = {
                    "type": "error",
                    "data": f"Invalid JSON in final buffer: {buffer}"
                }
                yield json.dumps(error_event) + "\n"

        # Send a completion event to signal the end of streaming
        try:
            completion_event = {
                "type": "completion",
                "data": "Stream completed"
            }
            yield json.dumps(completion_event) + "\n"

            # Wait for the task to complete and get the result
            await task
        except asyncio.CancelledError:
            # Handle task cancellation gracefully
            error_event = {
                "type": "info",
                "data": "Task was cancelled"
            }
            yield json.dumps(error_event) + "\n"
        except ConnectionError as e:
            # Handle connection errors specifically
            error_event = {
                "type": "error",
                "data": f"Connection error: {str(e)}"
            }
            yield json.dumps(error_event) + "\n"
        except Exception as e:
            # Handle any errors during task execution
            error_event = {
                "type": "error",
                "data": f"Task execution error: {str(e)}"
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
        if self.memory:
            return self.agent_with_chat_history.invoke(
                input={"input": message},
                config={"configurable": {"session_id": "ـ"}}
            )
        else:
            return self.agent_executor.invoke({"input": message})
