import os

from langchain import hub
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.agents import (
    AgentExecutor,
    create_openai_functions_agent,
    create_tool_calling_agent)

from src.agent.tools.shared_tools import init_llm
from src.agent.tools.tools_index import get_all_tools
from src.agent.tools.shared_tools import handle_exceptions, timeout


@tool
@handle_exceptions
def ethereum_blockchain_tool(query: str):
    """
    An tool for answering Ethereum blockchain-related queries and tasks. This function can:
    - Retrieve smart contract source code
    - Fetch contract ABIs (Application Binary Interface)
    - Get contract events and their details
    - Query contract transactions
    - Convert between timestamps and block numbers
    - Fetch wallet activities and transactions

    Args:
        query (str): Natural language query about Ethereum blockchain tasks.
            Examples:
            - "Get source code for contract 0x123..."
            - "Show me the ABI for contract 0x456..."
            - "Find events named Transfer from contract 0x789..."
            - "Get all transactions for contract 0xabc between blocks 1000-2000"

    Returns:
        str: Response containing the requested Ethereum blockchain information

    Raises:
        Web3ConnectionError: If unable to connect to Ethereum node
        ValueError: If the query cannot be parsed or contract address is invalid
    """

    llm = init_llm(service=os.environ["LLM_SERVICE"],
                   model_name=os.environ["LLM_MODEL"],
                   api_key=os.environ["LLM_API_KEY"],
                   stream=False)

    tools = get_all_tools(tools_path="eth_blockchain_function")

    if isinstance(llm, ChatOpenAI):
        prompt = hub.pull("pattern-agent/eth-agent")

        agent = create_openai_functions_agent(
            llm, tools, prompt)
    elif isinstance(llm, ChatOllama):
        prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(
            llm=llm, tools=tools, prompt=prompt)
    else:
        prompt = hub.pull("pattern-agent/eth-agent")

        agent = create_tool_calling_agent(
            llm=llm, tools=tools, prompt=prompt)

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
