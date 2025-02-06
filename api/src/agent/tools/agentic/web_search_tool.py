import os
from langchain.tools import tool

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

from src.agent.tools.shared_tools import handle_exceptions, timeout
from src.agent.tools.tools_index import get_all_tools


@tool
@handle_exceptions
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
    llm = ChatOpenAI(model="gpt-4o-mini")
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

    response = agent_executor.invoke({"input": query})

    try:
        tool_steps = {}
        for step in response["intermediate_steps"]:
            tool_steps["function_name"] = step[0].tool
            tool_steps["function_args"] = step[0].tool_input
            tool_steps["function_output"] = step[-1]
        return {"tool_response": response["output"], "tool_steps": tool_steps}
    except:
        return {"tool_response": response["output"]}
