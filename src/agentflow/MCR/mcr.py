import os
import json
import requests
from typing import List, Dict, Optional, Union


def get_mcr() -> List[Dict]:
    """
    Fetches MCR (Machine Comprehensible Resources) data from GraphQL endpoint
    and returns the list of MCR definitions.

    The function sends a GraphQL query to the EAS schema endpoint and processes
    the response to extract attestation data, which contains the MCR definitions.

    Returns:
        List[Dict]: List of MCR entries with their properties
    """
    # Get configuration from environment variables with defaults
    endpoint = os.getenv("MCR_GRAPHQL_ENDPOINT",
                         "https://sepolia.easscan.org/graphql")
    schema_id = os.getenv("MCR_SCHEMA_ID")

    query = """
    query {
      schema(where:{id:"%s"}) {
        attestations {
          id,
          decodedDataJson
        },
      }
    }
    """ % schema_id

    # Prepare the request
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}

    MCR = []

    try:
        # Send the GraphQL request
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for error responses

        data = response.json()

        # Process the response
        if "data" in data and "schema" in data["data"] and "attestations" in data["data"]["schema"]:
            attestations = data["data"]["schema"]["attestations"]

            for attestation in attestations:
                decoded_data = json.loads(attestation["decodedDataJson"])

                # Create a new MCR entry
                mcr_entry = {field["name"]: field["value"]["value"]
                             for field in decoded_data}

                # Add ID from attestation ID
                mcr_entry["ID"] = attestation["id"]

                # Add to MCR list
                MCR.append(mcr_entry)

        return MCR

    except requests.exceptions.RequestException as e:
        print(f"Error fetching MCR data: {e}")
        return MCR
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return MCR
    except Exception as e:
        print(f"Unexpected error: {e}")
        return MCR


def get_mcr_for_llm() -> List[Dict]:
    """
    Prepares MCR data in a format optimized for LLM consumption.

    Transforms the full MCR data into a simplified format containing only
    description, input/output schemas, and the DRI ID.

    Returns:
        List[Dict]: Simplified MCR data optimized for LLM consumption
    """
    MCR_FOR_LLM = []

    for DRI in get_mcr():
        MCR_FOR_LLM.append({
            "DESCRIPTION": DRI["DESCRIPTION"],
            "INPUT_SCHEMA": json.loads(str(DRI["INPUT_SCHEMA"])),
            "OUTPUT_SCHEMA": json.loads(str(DRI["OUTPUT_SCHEMA"])),
            "ID": DRI["ID"]
        })
    return MCR_FOR_LLM


def get_dri(id: str) -> Optional[Dict]:
    """
    Retrieves a specific MCR entry by its DRI ID.

    Args:
        id (str): The DRI ID to search for

    Returns:
        Dict or None: The MCR entry with the specified ID, or None if not found
    """
    for dri in get_mcr():
        if dri["ID"] == id:
            return dri
    return None


def authorize(data_source: str) -> Dict[str, str]:
    """
    Provides authorization headers for a specific data source.

    Args:
        data_source (str): The data source identifier (e.g., "MORALIS")

    Returns:
        Dict[str, str]: Dictionary with authorization headers
    """
    if data_source == "MORALIS":
        api_key = os.getenv("MORALIS_API_KEY")
        if not api_key:
            raise ValueError("MORALIS_API_KEY environment variable not set")
        return {
            "X-API-Key": api_key,
        }
    return {}


def get_base_url(data_source: str) -> str:
    """
    Returns the base URL for a given data source.

    Args:
        data_source (str): The data source identifier (e.g., "MORALIS")

    Returns:
        str: Base URL for the data source

    Raises:
        ValueError: If the data source is not supported
    """
    if data_source == "MORALIS":
        return "https://deep-index.moralis.io"
    else:
        raise ValueError(f"Unsupported data source: {data_source}")


def replace_variables(input_string: str, variables_dict: Dict[str, any]) -> str:
    """
    Replace all occurrences of ${variable_name} in the input string with values from the dictionary.

    Args:
        input_string (str): The input string containing variables in ${...} format
        variables_dict (dict): Dictionary containing variable names and their values

    Returns:
        str: The string with all variables replaced by their values
    """
    result = input_string

    for var_name, var_value in variables_dict.items():
        placeholder = "${" + var_name + "}"
        result = result.replace(placeholder, str(var_value))

    return result


def make_request(
    ID: str,
    input_data: Dict
) -> Union[Dict, Exception]:
    """
    Makes an HTTP request to a specified endpoint with given parameters based on DRI.

    Args:
        ID (str): The ID of Data Retrieval Instruction
        input_data (Dict): Input data for the request, used to populate variable placeholders

    Returns:
        Dict: JSON response from the API

    Raises:
        ValueError: If an unsupported data source is specified or DRI not found
        Exception: If any error occurs during the request process
    """
    try:
        dri = get_dri(ID)
        if not dri:
            raise ValueError(f"No DRI found with the given ID: {ID}")

        if dri["TYPE"] == "REST":
            endpoint = replace_variables(dri["ENDPOINT"], input_data)
            endpoint = json.loads(endpoint)

            method = endpoint["METHOD"]
            data_source = dri["DATASOURCE"]

            data = endpoint.get("QUERY", {})

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            # Add authorization headers
            headers.update(authorize(data_source.upper()))

            url = f"{get_base_url(data_source)}{endpoint['URL']}"

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=json.dumps(data) if data else None,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error making request: {e}")
        return e
