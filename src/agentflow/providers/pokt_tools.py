import re
import os
import json
import requests

from google import genai
from datetime import datetime
from google.genai import types
from langchain.tools import tool

from src.share.logging import Logging
from src.agentflow.utils.shared_tools import load_pokt_schema

# Get logger instance
logger = Logging().get_logger()

pokt_graphql = load_pokt_schema()


def extract_graphql_query(response_text):
    """
    Extract the GraphQL query from LLM response text.

    Args:
        response_text (str): The response text from the LLM.

    Returns:
        str: The extracted GraphQL query.
    """
    # Look for text between ```graphql and ``` or between ``` and ```
    pattern = r'```(?:graphql)?\s*([\s\S]*?)\s*```'
    matches = re.findall(pattern, response_text)

    if matches:
        return matches[0].strip()
    else:
        # If no code block, try to find a query block
        pattern = r'query\s*\{[\s\S]*?\}'
        matches = re.findall(pattern, response_text)
        if matches:
            return matches[0].strip()
        else:
            # Return the whole text if no specific query format found
            return response_text.strip()


def execute_graphql_query(query, variables=None):
    """
    Execute a GraphQL query against the POKT API.

    Args:
        query (str): The GraphQL query to execute.
        variables (dict, optional): Variables for the GraphQL query.

    Returns:
        dict: The response from the GraphQL API.
    """
    # GraphQL endpoint URL
    url = os.environ.get("POKT_GRAPH_ENDPOINT")
    if not url:
        logger.error("Environment variable 'POKT_GRAPH_ENDPOINT' is not set.")
        raise ValueError(
            "Environment variable 'POKT_GRAPH_ENDPOINT' is not set.")

    # Prepare the request payload
    payload = {
        "query": query,
    }

    if variables:
        payload["variables"] = variables

    # Set headers
    headers = {
        "Content-Type": "application/json"
    }

    api_key = os.environ.get("POKT_API_KEY")
    if not api_key:
        logger.error("Environment variable 'POKT_API_KEY' is not set.")
        raise ValueError("Environment variable 'POKT_API_KEY' is not set.")

    params = {
        "token": api_key
    }

    # Make the request
    try:
        logger.info(f"Executing GraphQL query: {query[:100]}...")
        response = requests.post(
            url, json=payload, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making GraphQL request: {e}")
        return {"error": str(e), "query": query}


def fix_graphql_query(pokt_graphql, user_task, graphql_query, error_response):
    """
    Attempt to fix a failed GraphQL query using AI.

    Args:
        pokt_graphql (str): The GraphQL schema.
        user_task (str): The original user task.
        graphql_query (str): The failed GraphQL query.
        error_response (str): The error response from the GraphQL API.

    Returns:
        str: A fixed GraphQL query.
    """
    # Initialize client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("Environment variable 'GEMINI_API_KEY' is not set.")
        raise ValueError("Environment variable 'GEMINI_API_KEY' is not set.")

    client = genai.Client(api_key=api_key)

    # Define the system prompt to help fix the query
    error_handling_system_prompt = f"""You are an expert programmer.
An graphql query was generated and executed but there is an error in the query. You need to fix the query and write a new query.

graphql schema is:
```graphql
{pokt_graphql}
```

user task is:
```text
{user_task}
```

graphql query is:
```graphql
{graphql_query}
```

error is:
```json
{error_response}
```
"""

    # Define system prompt configuration
    config = types.GenerateContentConfig(
        system_instruction=error_handling_system_prompt
    )

    try:
        logger.info("Attempting to fix GraphQL query with AI")
        # Ask the model to fix the query
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Please fix the GraphQL query to address the error.",
            config=config,
        )

        # Extract the fixed GraphQL query
        fixed_query = extract_graphql_query(response.text)
        logger.info("Generated fixed GraphQL query")
        return fixed_query
    except Exception as e:
        logger.error(f"Error trying to fix GraphQL query: {e}")
        # If we can't fix it, return the original query
        return graphql_query


@tool
def answer_pokt_query_task(user_task: str) -> str:
    """
    Answer a task using the POKT GraphQL API. The user task will be converted to a POKT GraphQL
    query and execute the query. Will attempt up to 3 times to fix query errors.

    Args:
        user_task (str): exact user task to be answered.

    Returns:
        str: The result of the task.
    """
    logger.info(f"Processing POKT query task: {user_task}")

    try:

        logger.info("Successfully loaded POKT GraphQL schema")

        # Create system prompt with current date
        system_prompt = f"""You are an expert programmer. Your given a graphql schema and you need to generate graphql query to answer user task.

        Pokt Date format in schema is YYYY-MM-DDTHH:mm:ss.SSSZ

        Today date is {datetime.now()}
        The graphql schema is:
        ```graphql
        {pokt_graphql}
        ```
        """

        # Initialize client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("Environment variable 'GEMINI_API_KEY' is not set.")
            return {"error": "Environment variable 'GEMINI_API_KEY' is not set."}

        client = genai.Client(api_key=api_key)

        # Define a system prompt to steer the model's behavior
        config = types.GenerateContentConfig(
            system_instruction=system_prompt
        )

        # Generate GraphQL query
        logger.info("Generating initial GraphQL query with Gemini")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_task,
            config=config,
        )

        # Extract the GraphQL query from the LLM response
        graphql_query = extract_graphql_query(response.text)
        logger.info(f"Generated GraphQL query: {graphql_query}")

        # Execute the GraphQL query with retry logic (max 3 attempts)
        max_attempts = 3
        attempt = 1

        while attempt <= max_attempts:
            logger.info(f"Query execution attempt {attempt}/{max_attempts}")
            result = execute_graphql_query(graphql_query)

            # Check if there's an error in the response
            if "errors" in result:
                logger.warning(
                    f"Attempt {attempt}/{max_attempts}: GraphQL query failed: {json.dumps(result.get('errors', {}))}")

                # If we've reached max attempts, return the error
                if attempt == max_attempts:
                    logger.error(
                        "Failed to execute query after maximum attempts")
                    return {
                        "error": "Failed to execute query after maximum attempts",
                        "last_error": result["errors"],
                        "last_query": graphql_query
                    }

                # Try to fix the query
                error_response = json.dumps(result.get("errors", {}))
                graphql_query = fix_graphql_query(
                    pokt_graphql, user_task, graphql_query, error_response)
                attempt += 1
            else:
                # Query succeeded, return the result
                logger.info("GraphQL query executed successfully")
                return result

        # Should never reach here due to the return in the loop
        return result
    except Exception as e:
        logger.error(f"Error in answer_pokt_query_task: {str(e)}")
        return {"error": str(e), "task": user_task}
