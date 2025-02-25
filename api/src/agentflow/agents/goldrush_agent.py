import os

from langchain import hub
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.agents import (
    AgentExecutor,
    create_openai_functions_agent,
    create_tool_calling_agent)

from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions, timeout
from src.agentflow.utils.shared_tools import init_llm, init_agent


@tool
@handle_exceptions
def goldrush_agent(query: str):
    """
    An agent for handling Ethereum blockchain-related queries and tasks.
    This agent can perform the following tasks:

    - Fetch wallet activity for a given address
    - fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address
    - Fetch the transactions involving an address including the decoded log events in a paginated fashion
    - Commonly used to fetch the earliest and latest transactions, and the transaction count for a wallet
    - Fetch and render a single transaction including its decoded event logs
    - Fetch a list of approvals across all token contracts categorized by spenders for a wallet’s assets

    Args:
        query (str): query about Ethereum blockchain tasks.

    Returns:
        str: Response containing the requested Ethereum blockchain information
    """
    llm = init_llm(service=os.environ["LLM_PROVIDER"],
                   model_name=os.environ["LLM_MODEL"],
                   api_key=os.environ["LLM_API_KEY"],
                   stream=False)

    tools = get_all_tools(tools_path="goldrush_tools")

    prompt = hub.pull("pattern-agent/eth-agent")

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
