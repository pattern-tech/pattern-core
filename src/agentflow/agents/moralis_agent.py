from langchain.tools import tool
from langchain.agents import AgentExecutor

from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions
from src.agentflow.utils.shared_tools import init_llm, init_agent, init_prompt


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
    config = Config.get_config()

    llm = init_llm(service=config["llm"]["provider"],
                   model_name=config["llm"]["model"],
                   api_key=config["llm"]["api_key"],
                   stream=False)

    tools = get_all_tools(tools_path="moralis_tools")

    prompt = init_prompt(llm, AgentType.BLOCKCHAIN_AGENT)

    agent = init_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        return_intermediate_steps=True,
        verbose=True)

    response = agent_executor.invoke({"input": query})

    try:
        agent_steps = []
        for step in response["intermediate_steps"]:
            agent_steps.append({
                "function_name": step[0].tool,
                "function_args": step[0].tool_input,
                "function_output": step[-1]
            })
        return {"agent_steps": agent_steps}
    except:
        return "no tools called inside agent"
