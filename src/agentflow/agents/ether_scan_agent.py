import os

from langchain.tools import tool
from langchain.agents import AgentExecutor
from langchain_community.callbacks.manager import get_openai_callback

from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType
from src.agentflow.utils.tools_index import get_all_tools
from src.agentflow.utils.shared_tools import handle_exceptions
from src.agentflow.utils.shared_tools import init_llm, init_agent, init_prompt


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
    - Call a read-only (view/pure) function of a smart contract and return its result.

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

    tools = get_all_tools(tools_path="ether_scan_tools")

    prompt = init_prompt(llm, AgentType.BLOCKCHAIN_AGENT)

    agent = init_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        return_intermediate_steps=True,
        verbose=True,
        stream_runnable=False)

    response = agent_executor.invoke({"input": query})

    try:
        agent_steps = []
        for step in response["intermediate_steps"]:
            agent_steps.append({
                "function_name": step[0].tool,
                "function_args": step[0].tool_input,
                "function_output": step[-1]
            })
        if agent_steps:
            return {"agent_steps": agent_steps}
        else:
            return {"agent_answer": response["output"]}
    except:
        return "no tools called inside agent"
