import os
import json
import requests

from langchain.tools import tool
from typing import List, Dict, Optional, Union
from src.share.logging import Logging

# Initialize logger
_logger = Logging().get_logger()


def get_mcr() -> List[Dict]:
    """
    Fetches MCR (Machine Comprehensible Resources) data from GraphQL endpoint
    and returns the list of MCR definitions.

    The function sends a GraphQL query to the EAS schema endpoint and processes
    the response to extract attestation data, which contains the MCR definitions.

    Returns:
        List[Dict]: List of MCR entries with their properties
    """
    _logger.info("Fetching MCR data from GraphQL endpoint")

    # Get configuration from environment variables with defaults
    endpoint = os.getenv("MCR_GRAPHQL_ENDPOINT",
                         "https://sepolia.easscan.org/graphql")
    schema_id = os.getenv("MCR_SCHEMA_ID")

    _logger.debug(f"Using endpoint: {endpoint}, schema_id: {schema_id}")

    query = """
    query {
        schema(where: {id: "%s"}) {
            attestations(where: {
            revoked: {
                equals: false
            }
            })
            {
            id
            decodedDataJson
            }
        }
}
    """ % schema_id

    # Prepare the request
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}

    MCR = []

    try:
        # Send the GraphQL request
        _logger.debug("Sending GraphQL request to fetch MCR data")
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for error responses

        data = response.json()

        _logger.debug("GraphQL response received successfully")

        # Process the response
        if "data" in data and "schema" in data["data"] and "attestations" in data["data"]["schema"]:
            attestations = data["data"]["schema"]["attestations"]
            _logger.info(f"Retrieved {len(attestations)} MCR attestations")

            for attestation in attestations:
                decoded_data = json.loads(attestation["decodedDataJson"])

                # Create a new MCR entry
                mcr_entry = {field["name"]: field["value"]["value"]
                             for field in decoded_data}

                # Add ID from attestation ID
                mcr_entry["ID"] = attestation["id"]

                # Add to MCR list
                MCR.append(mcr_entry)

        _logger.info(f"Processed {len(MCR)} MCR entries")
        return MCR

    except requests.exceptions.RequestException as e:
        _logger.error(f"Error fetching MCR data: {e}", exc_info=True)
        return MCR
    except json.JSONDecodeError as e:
        _logger.error(f"Error decoding JSON response: {e}", exc_info=True)
        return MCR
    except Exception as e:
        _logger.error(f"Unexpected error in get_mcr: {e}", exc_info=True)
        return MCR


def get_mcr_for_llm() -> List[Dict]:
    """
    Prepares MCR data in a format optimized for LLM consumption.

    Transforms the full MCR data into a simplified format containing only
    description, input/output schemas, and the DRI ID.

    Returns:
        List[Dict]: Simplified MCR data optimized for LLM consumption
    """
    _logger.info("Preparing MCR data for LLM consumption")
    MCR_FOR_LLM = []

    for DRI in get_mcr():
        MCR_FOR_LLM.append({
            "DESCRIPTION": DRI["DESCRIPTION"],
            "INPUT_SCHEMA": json.loads(DRI["INPUT_SCHEMA"]),
            "OUTPUT_SCHEMA": json.loads(DRI["OUTPUT_SCHEMA"]),
            "ID": DRI["ID"]
        })
    _logger.info(f"Prepared {len(MCR_FOR_LLM)} MCR entries for LLM")
    return MCR_FOR_LLM


def get_dri(id: str) -> Optional[Dict]:
    """
    Retrieves a specific MCR entry by its DRI ID.

    Args:
        id (str): The DRI ID to search for

    Returns:
        Dict or None: The MCR entry with the specified ID, or None if not found
    """
    _logger.debug(f"Looking up DRI with ID: {id}")
    for dri in get_mcr():
        if dri["ID"] == id:
            _logger.debug(f"Found DRI with ID: {id}")
            return dri
    _logger.warning(f"DRI with ID {id} not found")
    return None


def authenticate(data_source: str) -> Dict[str, str]:
    """
    Provides authentication headers for a specific data source.

    Args:
        data_source (str): The data source identifier (e.g., "MORALIS")

    Returns:
        Dict[str, str]: Dictionary with authenticate headers
    """
    _logger.debug(f"Generating authentication headers for {data_source}")
    if data_source == "MORALIS":
        api_key = os.getenv("MORALIS_API_KEY")
        if not api_key:
            _logger.error("MORALIS_API_KEY environment variable not set")
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
    _logger.debug(f"Getting base URL for data source: {data_source}")
    if data_source == "MORALIS":
        return "https://deep-index.moralis.io"
    else:
        _logger.error(f"Unsupported data source: {data_source}")
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
    _logger.debug("Replacing variables in template string")
    result = input_string

    for var_name, var_value in variables_dict.items():
        placeholder = "${" + var_name + "}"
        result = result.replace(placeholder, str(var_value))

    return result


@tool
def retrieve_data(ID: str, input_data: Dict) -> Dict:
    """
    Retrieve data from a specified data source using the provided DRI ID and input data.

    Args:
        ID (str): The ID of Data Retrieval Instruction
        input_data (Dict): Input data for the request, used to populate variable placeholders

    Returns:
        Dict: JSON response from the API
    """
    _logger.info(f"Retrieving data using DRI ID: {ID}")
    _logger.debug(f"Input data: {json.dumps(input_data)}")

    try:
        dri = get_dri(ID)
        if not dri:
            _logger.error(f"No DRI found with the given ID: {ID}")
            raise ValueError(f"No DRI found with the given ID: {ID}")

        if dri["TYPE"] == "REST":
            _logger.debug(f"Processing REST DRI: {ID}")
            endpoint = replace_variables(dri["ENDPOINT"], input_data)
            endpoint = json.loads(endpoint)

            method = endpoint["METHOD"]
            data_source = dri["DATA_SOURCE"]

            query_params = {}
            for param in endpoint.get("QUERY_PARAMS", []):
                param_name = param["name"]
                param_value = input_data.get(param_name, None)
                if param_value is not None:
                    query_params[param_name] = param_value

            data = endpoint.get("QUERY", {})
            _logger.debug(
                f"Prepared request - Method: {method}, Data source: {data_source}")

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            # Add authorization headers
            headers.update(authenticate(data_source.upper()))

            url = f"{get_base_url(data_source)}{endpoint['URL']}"
            _logger.info(f"Sending {method} request to {url}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=query_params,
                data=json.dumps(data) if data else None,
            )

            _logger.info(
                f"Received response with status code: {response.status_code}")
            if response.status_code != 200:
                _logger.warning(
                    f"Non-200 response: {response.status_code}, Content: {response.text[:200]}...")

            return {
                str(response.status_code): response.json() if response.status_code == 200 else response.text
            }

    except Exception as e:
        _logger.error(f"Error making request: {str(e)}", exc_info=True)
        return {"error": str(e)}
