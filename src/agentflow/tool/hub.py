from typing import List, Any

from src.agentflow.tool.tools_index import get_all_tools
from src.agentflow.tool.tool_selector import ToolSelector


class ToolRegistery:
    """
    A hub for managing and retrieving tools from various providers.
    Provides functionality to get all tools or select appropriate tools for a query.
    """

    providers = [
        "chain_scan",
        "moralis",
    ]

    _tool_selector = None

    @classmethod
    def _get_tool_selector(cls):
        """Get or initialize the tool selector."""
        if cls._tool_selector is None:
            cls._tool_selector = ToolSelector()
        return cls._tool_selector

    @classmethod
    def get_tools(cls):
        """Get all available tools from all providers."""
        tools = []
        for provider in cls.providers:
            tools.extend(get_all_tools(f"{provider}_tools"))
        return tools

    @classmethod
    def select_tools_for_query(cls, query: str) -> List[Any]:
        """
        Select appropriate tools for a given user query.

        Args:
            query (str): The user's query

        Returns:
            List[Any]: List of selected tool function references
        """
        # Get all available tools
        all_tools = cls.get_tools()

        # Use the tool selector to select appropriate tools
        selector = cls._get_tool_selector()
        selected_tools = selector.select_tools(query, all_tools)

        return selected_tools
