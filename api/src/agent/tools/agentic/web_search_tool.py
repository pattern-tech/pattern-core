import os
from langchain.tools import tool

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

from src.agent.tools.shared_tools import handle_exceptions, timeout
from src.agent.tools.tools_index import get_all_tools


@tool
@handle_exceptions
@timeout(seconds=70)
def web_search_tool(query: str):
    """
    A tool for searching the web using online and indexed search engines.
    - answering questions which needs web search using Tavily and Perplexity
    - get content of websites with their links
    - finding similar links

    Args:
        query (str): The search query string.

    Returns:
        str: Response containing the requested web search results.
    """
    llm = ChatOpenAI(model="gpt-4o")
    prompt = hub.pull("web-search-agent")

    tools = get_all_tools(tools_path="web_search_function")

    agent = create_openai_functions_agent(
        llm,
        tools,
        prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        return_intermediate_steps=True,
        verbose=True)

    input = f"utilize all available tools to provide a comprehensive response to the following query: {query}"

    response = agent_executor.invoke({"input": input})

    return {"tool_response": response["output"],
            "intermediate_steps": response["intermediate_steps"]}
