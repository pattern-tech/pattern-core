from langchain.tools import tool

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

from src.agent.tools.shared_tools import handle_exceptions, timeout
from src.agent.tools.tools_index import get_all_tools


@tool
@handle_exceptions
@timeout(seconds=60)
def ethereum_blockchain_tool(query: str):
    """
    A tool for handling Ethereum blockchain-related queries and tasks. This function can:
    - Retrieve smart contract source code
    - Fetch contract ABIs (Application Binary Interface)
    - Get contract events and their details
    - Query contract transactions
    - Convert between timestamps and block numbers

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

    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = hub.pull("pattern-agent/eth-agent")
    tools = get_all_tools(tools_path="eth_blockchain_function")

    agent = create_openai_functions_agent(
        llm,
        tools,
        prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        return_intermediate_steps=False,
        verbose=True)

    response = agent_executor.invoke({"input": query})

    return response["output"]
