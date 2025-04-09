# Standard library imports first
import json
from typing import List, Dict, Any, Optional, Callable

# Project imports
from src.util.configuration import Config
from src.agentflow.utils.shared_tools import init_llm


class ToolSelector:
    """
    A module that uses an LLM to select appropriate tools based on a user query.
    It analyzes the query and tool descriptions to determine which tools are most relevant.
    """

    def __init__(self):
        """Initialize the ToolSelector with an LLM."""
        config = Config.get_config()
        self.llm = init_llm(
            service=config["llm"]["provider"],
            model_name=config["llm"]["model"],
            api_key=config["llm"]["api_key"],
            stream=False,
            callbacks=None
        )

    def get_tool_descriptions(self, tools: List[Any]) -> List[Dict[str, str]]:
        """
        Extract name and description from each tool.

        Args:
            tools (List[Any]): List of tool function references

        Returns:
            List[Dict[str, str]]: List of dictionaries with tool name and description
        """
        tool_descriptions = []

        for tool in tools:
            # Extract name and docstring
            name = tool.name
            description = tool.description or "No description available"

            tool_descriptions.append({
                "name": name,
                "description": description
            })

        return tool_descriptions

    def select_tools(self, query: str, available_tools: List[Any]) -> List[Any]:
        """
        Select appropriate tools for a given user query.

        Args:
            query (str): The user's query
            available_tools (List[Any]): List of all available tool function references

        Returns:
            List[Any]: List of selected tool function references
        """
        # Get tool descriptions
        tool_descriptions = self.get_tool_descriptions(available_tools)

        # Create a prompt for the LLM
        prompt = self._create_tool_selection_prompt(query, tool_descriptions)

        # Get LLM response
        messages = [
            ("system", "You are a tool selection assistant. Your job is to analyze a user query and select the most appropriate tools to answer it."),
            ("human", prompt)
        ]

        response = self.llm.invoke(messages)

        # Parse the response to get selected tool names
        try:
            selected_tool_names = self._parse_tool_selection_response(
                response.content)

            # Filter the original tools list to return only selected tools
            selected_tools = [
                tool for tool in available_tools
                if tool.name in selected_tool_names
            ]

            return selected_tools
        except Exception as e:
            print(f"Error parsing tool selection response: {e}")
            # Return all tools as fallback if parsing fails
            return available_tools

    def _create_tool_selection_prompt(self, query: str, tool_descriptions: List[Dict[str, str]]) -> str:
        """
        Create a prompt for the LLM to select appropriate tools.

        Args:
            query (str): The user's query
            tool_descriptions (List[Dict[str, str]]): List of tool descriptions

        Returns:
            str: The prompt for the LLM
        """
        tools_json = json.dumps(tool_descriptions, indent=2)

        prompt = f"""
User Query: {query}

Available Tools:
{tools_json}

Instructions:
- Analyze the user query carefully
- Review each available tool and its description
- Select the tools that are directly relevant to answering the query
- If you are not sure if a tool is needed or not select it
- Return your answer as a JSON array of tool names, like this: ["tool_name1", "tool_name2"]
- If no tools are relevant, return an empty array: []
- Do not include any explanation or additional text, just the JSON array
- Break down the user task into smaller subtasks if needed

Selected Tools:
"""
        return prompt

    def _parse_tool_selection_response(self, response: str) -> List[str]:
        """
        Parse the LLM response to extract selected tool names.

        Args:
            response (str): The LLM's response

        Returns:
            List[str]: List of selected tool names
        """
        # Clean up the response to extract just the JSON part
        response = response.strip()

        # Handle potential formatting issues
        if not response.startswith('['):
            # Try to find the JSON array in the response
            start_idx = response.find('[')
            end_idx = response.rfind(']')

            if start_idx != -1 and end_idx != -1:
                response = response[start_idx:end_idx+1]
            else:
                # If no JSON array is found, return an empty list
                return []

        try:
            # Parse the JSON array
            selected_tools = json.loads(response)

            # Ensure it's a list of strings
            if isinstance(selected_tools, list) and all(isinstance(item, str) for item in selected_tools):
                return selected_tools
            else:
                return []
        except json.JSONDecodeError:
            # If parsing fails, return an empty list
            return []
