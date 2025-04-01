import os

from langchain.tools import tool
from src.agentflow.agents.base_agent import OraAgent
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions
from langchain_core.utils.function_calling import convert_to_openai_function


@tool
@handle_exceptions
def etherscan_agent(query: str):
    """
    An agent for handling Ethereum blockchain-related queries and tasks.
    This agent can perform the following tasks:

    - Get the current Unix timestamp
    - Convert a natural language date string into a Unix timestamp
    - Retrieve the source code of a smart contract
    - Retrieve the ABI of a smart contract
    - Retrieve the ABI of a specific event from a smart contract
    - Fetch events for a given smart contract event within a block range
    - Retrieve the latest Ethereum block number and hash
    - Convert a Unix timestamp to the nearest Ethereum block number
    - Decode the input data of an Ethereum transaction

    Args:
        query (str): query about Ethereum blockchain tasks.

    Returns:
        str: Response containing the requested Ethereum blockchain information
    """
    agent = OraAgent(os.environ["ORA_API_KEY"])

    tools = get_all_tools(tools_path="ether_scan_tools")

    openai_tools = [convert_to_openai_function(tool.func) for tool in tools]

    for tool, tool_def in zip(tools, openai_tools):
        tool_def = {"type": "function", "function": tool_def}
        agent.add_tool(tool_def, tool.func)

    result = agent.chat(query)

    return result