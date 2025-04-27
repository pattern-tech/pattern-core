import os
import ast
import json
import requests

from langchain.tools import tool
from typing import List, Dict, Optional, Union

from src.share.logging import Logging
from src.agentflow.MCR.authentication import APIKeyAuth
from src.agentflow.MCR.authentication import authenticate

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
            "TAG": DRI["TAG"],
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
    if os.getenv(f"{data_source}_BASE_URL" , None):
        return os.getenv(f"{data_source}_BASE_URL")
    else:
        _logger.error(f"Unsupported data source: {data_source}")
        raise ValueError(f"Unsupported data source: {data_source}. {data_source}_BASE_URL not set")


def replace_variables(input_string: str, variables_dict: Dict[str, any], input_schema: Dict[str, any]) -> str:
    """
    Replace all occurrences of ${variable_name} in the input string with values from the dictionary.

    Args:
        input_string (str): The input string containing variables in ${...} format
        variables_dict (dict): Dictionary containing variable names and their values
        input_schema (dict): The input schema containing type information for variables

    Returns:
        str: The string with all variables replaced by their values
    """
    if not variables_dict:
        return input_string

    # Split the input string to handle first part and rest separately
    parts = input_string.split(",", 1)
    first_part = parts[0]
    second_part = parts[1] if len(parts) > 1 else ""

    # Process each variable replacement
    for var_name, var_value in variables_dict.items():
        # Get variable type from schema if available
        var_type = input_schema.get(var_name, {}).get("type", None)

        # Replace in the first part (always as string without quotes)
        placeholder = f"${{{var_name}}}"
        first_part = first_part.replace(f"${{{var_name}}}", str(var_value))

        # Replace in the second part based on type
        if var_type == "string" and var_value is not None:
            # String values should not have quotes added
            second_part = second_part.replace(
                f"${{{var_name}}}", str(var_value))
        else:
            # Non-string values need to have their quotes removed
            second_part = second_part.replace(
                f'"${{{var_name}}}"', str(var_value))

    # Recombine the parts
    result = first_part + ("," + second_part if second_part else "")

    return result


def _validate_required_params(input_schema: Dict, input_data: Dict) -> List[str]:
    """
    Validates that all required parameters are present in the input data.

    Args:
        input_schema (Dict): Schema defining required parameters
        input_data (Dict): User provided input data

    Returns:
        List[str]: List of missing parameter names, empty if all required params are present
    """
    missing_params = []
    if "required" in input_schema and isinstance(input_schema["required"], list):
        for required_param in input_schema["required"]:
            if required_param not in input_data:
                missing_params.append(required_param)
    return missing_params


def _process_rest_dri(dri: Dict, input_data: Dict, input_schema: Dict) -> Dict:
    """
    Process a REST DRI request.

    Args:
        dri (Dict): The DRI definition
        input_data (Dict): User provided input data
        input_schema (Dict): Schema for input validation

    Returns:
        Dict: API response or error message
    """
    _logger.debug(f"Processing REST DRI: {dri['ID']}")

    try:
        # Replace variables in endpoint definition
        endpoint_str = replace_variables(
            dri["ENDPOINT"], input_data, input_schema)

        endpoint = ast.literal_eval(endpoint_str)

        # Extract request parameters
        method = endpoint.get("METHOD", "GET")
        data_source = dri["DATA_SOURCE"]

        # Prepare request parameters
        url = f"{get_base_url(data_source)}{endpoint['URL']}"
        query_params = endpoint.get("QUERY_PARAMS")
        body = endpoint.get("BODY")

        # remove keys with None values
        query_params = {k: v for k, v in query_params.items(
        ) if v is not None} if query_params else None
        body = {k: v for k, v in body.items() if v is not None} if body else None

        # Get authentication for the data source
        auth = authenticate(data_source.upper())

        headers = {
            "Content-Type": "application/json"
        }

        _logger.info(f"Sending {method} request to {url}")
        _logger.info(
            f"Query params: {json.dumps(query_params) if query_params else 'None'}")
        _logger.info(f"Request body: {json.dumps(body) if body else 'None'}")

        # Make the request
        response = requests.request(
            method=method,
            url=url,
            params=query_params,
            data=body,
            auth=auth,
            headers=headers,
            timeout=30  # Add timeout for safety
        )

        _logger.info(
            f"Received response with status code: {response.status_code}")

        # Handle response based on status code
        if response.status_code != 200:
            _logger.warning(
                f"Non-200 response: {response.status_code}, Content: {response.text[:200]}...")

        # Try to parse as JSON, fall back to text if that fails
        try:
            response_data = response.json() if response.status_code == 200 else response.text
        except json.JSONDecodeError:
            response_data = response.text

        return {str(response.status_code): response_data}

    except Exception as e:
        error_msg = f"Error processing REST DRI: {str(e)}"
        _logger.error(error_msg, exc_info=True)
        return {"error": error_msg}


@tool
def retrieve_data(ID: str, input_data: Dict = None) -> Dict:
    """
    Retrieve data from a specified data source using the provided DRI ID and input data.

    Args:
        ID (str): The ID of instruction to retrieve data
        input_data (Dict, optional): actual data which should be passed according to the input schema

    Returns:
        Dict: JSON response from the DRI or error message
    """
    _logger.info(f"Retrieving data using DRI ID: {ID}")

    # Initialize input_data if None
    input_data = input_data or {}
    _logger.debug(f"Input data: {json.dumps(input_data)}")

    try:
        # Get DRI definition
        dri = get_dri(ID)
        if not dri:
            error_msg = f"No DRI found with the given ID: {ID}"
            _logger.error(error_msg)
            return {"error": error_msg}

        # Parse input schema
        input_schema = json.loads(dri["INPUT_SCHEMA"])

        # Validate required parameters
        if missing_params := _validate_required_params(input_schema, input_data):
            error_msg = f"Missing required parameters: {', '.join(missing_params)}. Please provide these parameters."
            _logger.warning(error_msg)
            return {"error": error_msg}

        # Process REST DRI
        if dri["TYPE"] == "REST":
            return _process_rest_dri(dri, input_data, input_schema)

        # Handle other DRI types if implemented in the future
        return {"error": f"Unsupported DRI type: {dri['TYPE']}"}

    except Exception as e:
        _logger.error(
            f"Error processing retrieve_data: {str(e)}", exc_info=True)
        return {"error": str(e)}
