from web3 import Web3
import os
import ast
import json
import requests
import psycopg2
import sshtunnel

from langchain.tools import tool
from sshtunnel import SSHTunnelForwarder
from typing import List, Dict, Optional, Union, Any

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


def get_mcr_from_db() -> List[Dict]:
    """
    Fetches MCR (Machine Comprehensible Resources) data from PostgreSQL database
    and returns the list of MCR definitions.

    The function connects to the database using credentials from environment variables
    and retrieves all records from the instructions table.

    Returns:
        List[Dict]: List of MCR entries with their properties
    """
    _logger.info("Fetching MCR data from PostgreSQL database")

    MCR = []

    # Get database configuration from environment variables
    db_host = os.getenv("MCR_DB_HOST")
    db_port = int(os.getenv("MCR_DB_PORT", "5432"))
    db_name = os.getenv("MCR_DB_NAME")
    db_username = os.getenv("MCR_DB_USERNAME")
    db_password = os.getenv("MCR_DB_PASSWORD")

    # Check if any of the required environment variables are missing
    missing_env_vars = []
    if not db_host:
        missing_env_vars.append("MCR_DB_HOST")
    if not db_name:
        missing_env_vars.append("MCR_DB_NAME")
    if not db_username:
        missing_env_vars.append("MCR_DB_USERNAME")
    if not db_password:
        missing_env_vars.append("MCR_DB_PASSWORD")

    if missing_env_vars:
        _logger.error(
            f"Missing required environment variables: {', '.join(missing_env_vars)}")
        return MCR

    # Get SSH tunnel configuration if needed
    ssh_host = os.getenv("MCR_SSH_HOST")
    ssh_port = int(os.getenv("MCR_SSH_PORT", "22")
                   ) if os.getenv("MCR_SSH_PORT") else 22
    ssh_username = os.getenv("MCR_SSH_USERNAME")

    # Only use SSH tunnel if all required SSH settings are provided
    ssh_tunnel = ssh_host is not None and ssh_username is not None

    # Setup SSH tunnel if configured
    tunnel = None
    connection_host = db_host
    connection_port = db_port

    try:
        if ssh_tunnel:
            _logger.info(f"Setting up SSH tunnel to {ssh_host}:{ssh_port}")
            tunnel = SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_username=ssh_username,
                remote_bind_address=(db_host, db_port),
                local_bind_address=('localhost', db_port)
            )

            # Start the SSH tunnel with detailed error capture
            try:
                tunnel.start()
                if tunnel.is_active:
                    _logger.info(
                        f"SSH tunnel established successfully at localhost:{tunnel.local_bind_port}")
                    # Update connection parameters to use tunnel
                    connection_host = 'localhost'
                    connection_port = tunnel.local_bind_port
                else:
                    _logger.error(
                        "Failed to establish SSH tunnel - tunnel is not active")
                    return MCR
            except Exception as ssh_err:
                _logger.error(
                    f"SSH tunnel error: {str(ssh_err)}", exc_info=True)
                return MCR
        else:
            _logger.info(
                f"Connecting directly to database at {db_host}:{db_port}")

        # Connect to the database with detailed error logging
        _logger.info(
            f"Connecting to PostgreSQL at {connection_host}:{connection_port}...")
        try:
            conn = psycopg2.connect(
                host=connection_host,
                port=connection_port,
                database=db_name,
                user=db_username,
                password=db_password,
                # Add connection timeout to avoid hanging
                connect_timeout=10
            )
            _logger.info("Database connection established successfully")
        except psycopg2.OperationalError as db_err:
            _logger.error(
                f"Failed to connect to database: {str(db_err)}", exc_info=True)
            return MCR

        # Create a cursor object
        cursor = conn.cursor()

        # Execute query to fetch all records from instructions table
        _logger.info(
            "Executing SQL query to fetch MCR data from instructions table")

        # Check if the table exists first
        try:
            cursor.execute("SELECT to_regclass('public.instructions')")
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                _logger.error(
                    "Table 'instructions' does not exist in the database")
                return MCR
        except psycopg2.Error as table_err:
            _logger.error(f"Error checking if table exists: {str(table_err)}")
            return MCR

        # Get the actual column names to verify case sensitivity
        try:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'instructions'
            """)
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            # Reset connection state in case of any previous errors
            conn.rollback()
        except psycopg2.Error as col_err:
            _logger.error(f"Error fetching column info: {str(col_err)}")
            conn.rollback()

        # Execute main query using the exact column case from the database metadata
        try:
            # Build query using the actual column names from schema instead of assuming case
            # Most PostgreSQL columns are usually case-insensitive, but we'll match exactly
            query = """
                SELECT
                    id,
                    "TAGS",
                    "SCHEMA_VERSION",
                    "TYPE",
                    "DATA_SOURCE",
                    "DESCRIPTION",
                    "ENDPOINT",
                    "INPUT_SCHEMA",
                    "OUTPUT_SCHEMA"
                FROM instructions
            """
            cursor.execute(query)

            # Fetch all records
            records = cursor.fetchall()
            _logger.info(f"Retrieved {len(records)} MCR records from database")

            # Process each record
            for record in records:
                mcr_entry = {
                    # Convert ID to string for consistency with get_mcr()
                    "ID": str(record[0]),
                    "TAGS": record[1],
                    "SCHEMA_VERSION": record[2],
                    "TYPE": record[3],
                    "DATA_SOURCE": record[4],
                    "DESCRIPTION": record[5],
                    "ENDPOINT": record[6],
                    "INPUT_SCHEMA": record[7],
                    "OUTPUT_SCHEMA": record[8] if len(record) > 8 and record[8] else "{}"
                }

                # Add to MCR list
                MCR.append(mcr_entry)

        except psycopg2.Error as query_err:
            _logger.error(f"SQL query error: {str(query_err)}")
            conn.rollback()

            # Try a simpler query that simply gets all columns
            _logger.info("Trying fallback query to get all columns")
            try:
                cursor.execute("SELECT * FROM instructions")

                # Fetch all records and column names from cursor description
                records = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                _logger.info(f"Fallback query column names: {column_names}")
                _logger.info(
                    f"Fallback query retrieved {len(records)} MCR records")

                # Get the index of required columns
                id_idx = column_names.index('id') if 'id' in column_names else column_names.index(
                    'ID') if 'ID' in column_names else 0
                tag_idx = -1
                schema_version_idx = -1
                type_idx = -1
                data_source_idx = -1
                description_idx = -1
                endpoint_idx = -1
                input_schema_idx = -1
                output_schema_idx = -1

                # Try to find columns by case-insensitive comparisons
                for idx, col_name in enumerate(column_names):
                    if col_name.upper() == 'TAGS':
                        tag_idx = idx
                    elif col_name.upper() == 'SCHEMA_VERSION':
                        schema_version_idx = idx
                    elif col_name.upper() == 'TYPE':
                        type_idx = idx
                    elif col_name.upper() == 'DATA_SOURCE':
                        data_source_idx = idx
                    elif col_name.upper() == 'DESCRIPTION':
                        description_idx = idx
                    elif col_name.upper() == 'ENDPOINT':
                        endpoint_idx = idx
                    elif col_name.upper() == 'INPUT_SCHEMA':
                        input_schema_idx = idx
                    elif col_name.upper() == 'OUTPUT_SCHEMA':
                        output_schema_idx = idx

                # Process each record from fallback query
                for record in records:
                    mcr_entry = {
                        "ID": str(record[id_idx]),
                        "TAGS": record[tag_idx] if tag_idx >= 0 and tag_idx < len(record) else "",
                        "SCHEMA_VERSION": record[schema_version_idx] if schema_version_idx >= 0 and schema_version_idx < len(record) else "",
                        "TYPE": record[type_idx] if type_idx >= 0 and type_idx < len(record) else "",
                        "DATA_SOURCE": record[data_source_idx] if data_source_idx >= 0 and data_source_idx < len(record) else "",
                        "DESCRIPTION": record[description_idx] if description_idx >= 0 and description_idx < len(record) else "",
                        "ENDPOINT": record[endpoint_idx] if endpoint_idx >= 0 and endpoint_idx < len(record) else "",
                        "INPUT_SCHEMA": record[input_schema_idx] if input_schema_idx >= 0 and input_schema_idx < len(record) else "{}",
                        "OUTPUT_SCHEMA": record[output_schema_idx] if output_schema_idx >= 0 and output_schema_idx < len(record) else "{}"
                    }

                    # Add to MCR list
                    MCR.append(mcr_entry)
            except psycopg2.Error as fallback_err:
                _logger.error(f"Fallback query error: {str(fallback_err)}")
                conn.rollback()

        # Close the cursor and connection
        cursor.close()
        conn.close()
        _logger.info("Database connection closed")

        return MCR

    except psycopg2.Error as e:
        _logger.error(f"PostgreSQL Error: {str(e)}", exc_info=True)
        return MCR
    except sshtunnel.BaseSSHTunnelForwarderError as e:
        _logger.error(f"SSH Tunnel Error: {str(e)}", exc_info=True)
        return MCR
    except Exception as e:
        _logger.error(
            f"Unexpected error in get_mcr_from_db: {str(e)}", exc_info=True)
        return MCR
    finally:
        # Close the SSH tunnel if it was opened
        if tunnel is not None and tunnel.is_active:
            tunnel.close()
            _logger.info("SSH tunnel closed")


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

    for DRI in get_mcr_from_db():
        MCR_FOR_LLM.append({
            "DESCRIPTION": DRI["DESCRIPTION"],
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
    for dri in get_mcr_from_db():
        if dri["ID"] == id:
            _logger.debug(f"Found DRI with ID: {id}")
            return dri
    _logger.warning(f"DRI with ID {id} not found")
    return None


def get_base_url(data_source: str) -> str:
    """
    Returns the base URL for a given data source.

    Args:
        data_source (str): The data source identifier 

    Returns:
        str: Base URL for the data source

    Raises:
        ValueError: If the data source is not supported
    """
    data_source = "_".join(data_source.upper().split())

    _logger.debug(f"Getting base URL for data source: {data_source}")
    if os.getenv(f"{data_source}_BASE_URL", None):
        return os.getenv(f"{data_source}_BASE_URL")
    else:
        _logger.error(f"Unsupported data source: {data_source}")
        raise ValueError(
            f"Unsupported data source: {data_source}. {data_source}_BASE_URL not set")


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


# -------------------------
# contract function call
# -------------------------


def _get_chain_config(chain_id: str) -> Dict:
    _config = {}
    if chain_id == "1":
        _config["RPC"] = os.environ["ETH_RPC"]
        _config["URL"] = "https://api.etherscan.io/v2/api"
        _config["API_KEY"] = os.environ["ETHER_SCAN_API_KEY"]
    elif chain_id == "42161":
        _config["RPC"] = os.environ["ARBITRUM_ONE_RPC"]
        _config["URL"] = "https://api.arbiscan.io/api"
        _config["API_KEY"] = os.environ["ARBI_SCAN_API_KEY"]
    elif chain_id == "8453":
        _config["RPC"] = os.environ["BASE_RPC"]
        _config["URL"] = "https://api.basescan.org/api"
        _config["API_KEY"] = os.environ["BASE_SCAN_API_KEY"]
    elif chain_id == "137":
        _config["RPC"] = os.environ["POLYGON_RPC"]
        _config["URL"] = "https://api.polygonscan.com/api"
        _config["API_KEY"] = os.environ["POLYGON_SCAN_API_KEY"]
    elif chain_id == "250":
        _config["RPC"] = os.environ["FANTOM_RPC"]
        _config["URL"] = "https://api.ftmscan.com/api"
        _config["API_KEY"] = os.environ["FTM_SCAN_API_KEY"]
    else:
        raise ValueError(f"Invalid chain ID: {chain_id}")

    return _config


def fetch_contract_source_code(contract_address: str, chain_id: str, api_key: str) -> str:
    """
    Retrieve the source code of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250
        api_key (str): The decrypted Etherscan API key.

    Returns:
        str: The contract source code.
    """
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    return response.json()["result"][0]


def fetch_contract_abi(contract_address: str, chain_id: str, api_key: str) -> Dict:
    """
    Retrieve the ABI of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250
        api_key (str): The decrypted Etherscan API key.

    Returns:
        Dict: A dictionary representing the contract ABI.
    """
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": api_key
    }
    response = requests.get(url, params=params)

    result = response.json().get("result")
    if result is None:
        raise Exception("No ABI found for the contract.")

    return json.loads(result)


@tool
def get_contract_abi(contract_address: str, chain_id: str) -> Dict:
    """
    Retrieve the ABI of a smart contract.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250

    Returns:
        Dict: The contract ABI.
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]

    final_output = {"proxy": [], "implementation": []}

    response = fetch_contract_source_code(contract_address, chain_id, api_key)

    current_address = contract_address
    while int(response.get('Proxy', 0)):
        final_output["proxy"].append(json.loads(response["ABI"]))
        current_address = response["Implementation"]
        response = fetch_contract_source_code(
            current_address, chain_id, api_key)

    final_output["implementation"].append(json.loads(response["ABI"]))

    return final_output


@tool
def call_contract_function(contract_address: str, chain_id: str, function_name: str, function_params: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Call a read-only (view/pure) function of a smart contract and return its result to get data from contract

    Args:
        contract_address (str): The address of the smart contract.
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250
        function_name (str): The name of the function to call.
        function_params (Optional[List[Any]]): List of parameters to pass to the function. Default is None (no parameters).

    Returns:
        Dict[str, Any]: A dictionary containing the following fields:
            - success: Boolean indicating if the call was successful
            - result: The result of the function call if successful
            - error: Error message if unsuccessful
            - result_type: The data type of the result

    Raises:
        Exception: If the contract ABI cannot be retrieved or the function call fails
    """
    # Initialize parameters if None
    if function_params is None:
        function_params = []

    api_key = _get_chain_config(chain_id)["API_KEY"]
    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

    try:
        # Get the contract ABI
        contract_address = Web3.to_checksum_address(contract_address)
        implementation_contract_address = contract_address
        # Check if the contract address is a proxy and get the implementation address
        if int(fetch_contract_source_code(contract_address, chain_id, api_key).get('Proxy', 0)):
            implementation_contract_address = fetch_contract_source_code(
                contract_address, chain_id, api_key)["Implementation"]
            implementation_contract_address = Web3.to_checksum_address(
                implementation_contract_address)

        abi = fetch_contract_abi(
            implementation_contract_address, chain_id, api_key)

        contract = web3.eth.contract(address=contract_address, abi=abi)

        # Find the function in the ABI
        function_entries = [f for f in abi if f.get(
            'type') == 'function' and f.get('name') == function_name]
        if not function_entries:
            available_functions = [f['name']
                                   for f in abi if f.get('type') == 'function']
            raise Exception(
                f"Function '{function_name}' not found in contract ABI. Available functions: {available_functions}")

        # Get the function object
        function_obj = getattr(contract.functions, function_name)

        # Check if the function is read-only
        function_entry = function_entries[0]
        if function_entry.get('stateMutability') not in ['view', 'pure', 'constant']:
            raise Exception(
                f"Function '{function_name}' is not a read-only function and might modify state or require a transaction.")

        # Get function outputs for later use
        function_outputs = function_entry.get('outputs', [])

        # Call the function with provided parameters
        result = function_obj(*function_params).call()

        # Process the result
        result_type = "unknown"
        processed_result = result

        # Determine result type and format accordingly
        if isinstance(result, (int, float, bool, str)):
            result_type = type(result).__name__
        elif isinstance(result, bytes):
            processed_result = web3.to_hex(result)
            result_type = "bytes (hex)"
        # Handle both tuple and list results - Web3.py may return either depending on the version
        elif isinstance(result, (tuple, list)):
            # If we have output definitions, create a dictionary with proper names
            if function_outputs and len(function_outputs) == len(result):
                processed_result = {}
                for i, output in enumerate(function_outputs):
                    output_name = output.get('name')
                    if not output_name:  # If name is empty, use index
                        output_name = f"output_{i}"

                    value = result[i]
                    processed_result[output_name] = value

                    # Handle special types
                    if isinstance(value, bytes):
                        processed_result[output_name] = web3.to_hex(value)
                    # For large integers, preserve the original value
                    # but also provide the ether conversion for convenience
                    elif isinstance(value, int) and value > 10**10:
                        processed_result[f"{output_name}_eth"] = web3.from_wei(
                            value, 'ether')

                result_type = "struct"
            else:
                # Fallback to list if we can't match outputs
                processed_result = list(result)
                processed_result = [web3.to_hex(v) if isinstance(
                    v, bytes) else v for v in processed_result]
                result_type = "tuple"

        response = {
            "success": True,
            "result": processed_result,
            "result_type": function_outputs,
        }

        return response

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None,
            "result_type": None
        }
