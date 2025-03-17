from langchain.tools import tool
from langchain.agents import AgentExecutor

from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions
from src.agentflow.utils.shared_tools import init_llm, init_agent, init_prompt


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
    config = Config.get_config()

    llm = init_llm(service=config["llm"]["provider"],
                   model_name=config["llm"]["model"],
                   api_key=config["llm"]["api_key"],
                   stream=False)

    tools = get_all_tools(tools_path="goldrush_tools")

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
