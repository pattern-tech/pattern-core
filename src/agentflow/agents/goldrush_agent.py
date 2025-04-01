import os

from langchain.tools import tool
from src.agentflow.agents.base_agent import OraAgent
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions
from langchain_core.utils.function_calling import convert_to_openai_function

@tool
@handle_exceptions
def goldrush_agent(query: str):
    """
    An agent for handling Ethereum blockchain-related queries and tasks.
    This agent can perform the following tasks:

    - Get activity across all chains for address
    - fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address
    - Fetch transactions for a given wallet address (paginated)
    - Fetch a summary of transactions (earliest and latest) for a given wallet address.
    - Fetch a single transaction including its decoded event logs
    - Fetch list of approvals across all token contracts categorized by spenders for a wallet’s assets

    Args:
        query (str): query about Ethereum blockchain tasks.

    Returns:
        str: Response containing the requested Ethereum blockchain information
    """
    agent = OraAgent(os.environ["ORA_API_KEY"])

    tools = get_all_tools(tools_path="goldrush_tools")

    openai_tools = [convert_to_openai_function(tool.func) for tool in tools]

    for tool, tool_def in zip(tools, openai_tools):
        tool_def = {"type": "function", "function": tool_def}
        agent.add_tool(tool_def, tool.func)

    result = agent.chat(query)

    return result