import os
import json

from langchain.tools import tool
from src.agentflow.agents.base_agent import OraAgent
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions
from langchain_core.utils.function_calling import convert_to_openai_function


@tool
@handle_exceptions
def moralis_agent(query: str):
    """
    An agent for handling Ethereum blockchain-related queries and tasks.
    This agent can perform the following tasks:

    - Get active chains for a wallet address across all chains
    - Get token balances for a specific wallet address and their token prices in USD. (paginated)
    - Get the stats for a wallet address.
    - Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers and contract interactions.
    - Get the contents of a transaction by the given transaction hash.
    - Get ERC20 approvals for one or many wallet addresses and/or contract addresses, ordered by block number in descending order.

    Args:
        query (str): query about Ethereum blockchain tasks.

    Returns:
        str: Response containing the requested Ethereum blockchain information
    """
    agent = OraAgent(os.environ["ORA_API_KEY"])

    tools = get_all_tools(tools_path="moralis_tools")

    openai_tools = [convert_to_openai_function(tool.func) for tool in tools]

    for tool, tool_def in zip(tools, openai_tools):
        tool_def = {"type": "function", "function": tool_def}
        agent.add_tool(tool_def, tool.func)

    # Pretty-print the tools for debugging
    print(json.dumps(agent.tools, indent=2))

    result = agent.chat(query)

    return result
