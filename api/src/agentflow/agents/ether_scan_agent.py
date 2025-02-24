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
def etherscan_agent(query: str):
    """
    An agent for handling Ethereum blockchain-related queries and tasks. This agent has access to these tools:

    - get_current_timestamp : Get the current Unix timestamp
    - convert_to_timestamp : Convert a natural language date string into a Unix timestamp
    - get_contract_source_code : Retrieve the source code of a smart contract
    - get_contract_abi : Retrieve the ABI of a smart contract
    - get_abi_of_event : Retrieve the ABI of a specific event from a smart contract
    - get_contract_events : Fetch events for a given smart contract event within a block range
    - get_latest_eth_block_number : Retrieve the latest Ethereum block number
    - convert_timestamp_to_block_number : Convert a Unix timestamp to the nearest Ethereum block number

    Args:
        query (str): query about Ethereum blockchain tasks.

    Returns:
        str: Response containing the requested Ethereum blockchain information
    """
    llm = init_llm(service=os.environ["LLM_PROVIDER"],
                   model_name=os.environ["LLM_MODEL"],
                   api_key=os.environ["LLM_API_KEY"],
                   stream=False)

    tools = get_all_tools(tools_path="ether_scan_tools")

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
