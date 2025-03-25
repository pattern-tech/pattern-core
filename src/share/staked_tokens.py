import json
import requests

from typing import List, Dict, Union


def aggregate_result(results: List[Dict]) -> List[Dict]:
    """
    Merge a list of dictionaries by summing values for common keys.

    Parameters:
        dict_list (list): A list of dictionaries with numeric values.

    Returns:
        dict: A merged dictionary with summed values for duplicate keys.
    """
    aggregated = {}

    for sublist in results:
        for record in sublist:
            address = record.get("address")
            staked_str = record.get("staked", "0")
            try:
                staked = int(staked_str)
            except ValueError:
                staked = 0  # fallback if conversion fails

            aggregated[address] = aggregated.get(address, 0) + staked
    return aggregated


def get_morpheus_stakers(
    builders_project_id: str = "0xdcba960308192a0eb3e6dbd97b27b3cc2454e38d06ef78ced76e7378afb2e5dc",
    first: int = 1000,
    skip: int = 0,
) -> List[Dict[str, Union[str, int, float, str]]]:
    """
    Fetches users for a given Builders project.

    Args:
        builders_project_id (str, optional): The ID of the Builders project. Defaults to "0xdcba960308192a0eb3e6dbd97b27b3cc2454e38d06ef78ced76e7378afb2e5dc".
        first (int, optional): The number of users to fetch. Defaults to 5.
        skip (int, optional): The number of users to skip. Defaults to 0.

    Returns:
        List[Dict[str, Union[str, int, float, str]]]: A list of dictionaries containing user data.
    """
    results = []

    # BASE chain
    payload = {
        "operationName": "getBuildersProjectUsers",
        "variables": {
            "first": first,
            "skip": skip,
            "buildersProjectId": builders_project_id
        },
        "query": "query getBuildersProjectUsers($first: Int = 10, $skip: Int = 10, $buildersProjectId: Bytes = \"\") {\n  buildersUsers(\n    first: $first\n    skip: $skip\n    where: {buildersProject_: {id: $buildersProjectId}}\n  ) {\n    address\n    id\n    staked\n    lastStake\n    __typename\n  }\n}"
    }
    url = "https://subgraph.satsuma-prod.com/8675f21b07ed/9iqb9f4qcmhosiruyg763--465704/morpheus-mainnet-base/api"
    response = requests.post(url, data=json.dumps(payload))
    results.append(response.json()["data"]["buildersUsers"])

    # ARBITRUM chain
    url = "https://api.studio.thegraph.com/query/73688/lumerin-node/version/latest"

    headers = {
        "content-type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    results.append(response.json()["data"]["buildersUsers"])

    return aggregate_result(results)


def get_user_staked_tokens(wallet_address: str, provider: str) -> List[Dict[str, Union[str, int, float, str]]]:
    """
    Fetches staked tokens for a given user.

    Args:
        wallet_address (str): The address of the user.

    Returns:
        List[Dict[str, Union[str, int, float, str]]]: A list of dictionaries containing staked token data.
    """
    if provider == "morpheus":
        holders = get_morpheus_stakers()
        return holders.get(wallet_address, 0)
    else:
        raise NotImplementedError(f"{provider} not implemented")
