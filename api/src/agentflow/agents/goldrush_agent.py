import os

from langchain import hub
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.agents import (
    AgentExecutor,
    create_openai_functions_agent,
    create_tool_calling_agent)

from src.agent.tools.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions, timeout
from src.agentflow.utils.shared_tools import init_llm, init_agent_and_prompt


@tool
@handle_exceptions
def goldrush_agent(query: str):
    """
    An agent for handling Ethereum blockchain-related queries and tasks. This agent has access to these tools:

    - get_wallet_activity :  Fetch wallet activity for a given address
    - get_balance_for_address : fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address
    - get_wallet_transactions : Fetch the transactions involving an address including the decoded log events in a paginated fashion
    - get_transactions_summary : Commonly used to fetch the earliest and latest transactions, and the transaction count for a wallet
    - get_transaction_detail :  Fetch and render a single transaction including its decoded event logs
    - get_token_approvals : Fetch a list of approvals across all token contracts categorized by spenders for a wallet’s assets

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

    agent, prompt = init_agent_and_prompt(llm)

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
