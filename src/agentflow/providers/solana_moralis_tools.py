"""
MORALIS API v2.2
"""
import requests

from moralis import evm_api
from langchain.tools import tool

from src.util.configuration import Config
from src.util.exceptions import NotSupportedError
from src.agentflow.utils.shared_tools import handle_exceptions

_config = Config.get_config()
_moralis_config = Config.get_service_config(_config, "MORALIS")

_MORALIS_SOLANA_URL = "https://solana-gateway.moralis.io"


def check_solana_network_supported(network: str) -> bool:
    """
    Moralis supported Solana networks
    """
    supported_networks = ["mainnet", "devnet"]
    if network in supported_networks:
        return True
    raise NotSupportedError(
        f"Solana network {network} is not supported. Supported networks are: {supported_networks}")


@tool
@handle_exceptions
def get_solana_token_pairs(token_address: str, network: str = "mainnet", output_include: list[str] = None, cursor: str = "", limit: int = 50) -> dict:
    """
    Get the supported pairs for a specific Solana token address.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        cursor (str): The cursor returned in the previous response (for pagination)
        limit (int): The number of results per page (default: 50, max: 50)

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - cursor: The pagination cursor for the next set of results
            - pageSize: Number of results per page
            - page: Current page number
            - pairs: List of token pairs where each dictionary contains:
              - exchangeAddress: The exchange address
              - exchangeName: The exchange name
              - exchangeLogo: Exchange logo URL
              - pairAddress: Pair contract address
              - pairLabel: Pair label (e.g., "SOL/USDC")
              - usdPrice: Current price in USD
              - liquidityUsd: Liquidity in USD
              - pair: Array with token details
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/{token_address}/pairs"

    params = {}
    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token pairs. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_pairs = []
    for pair in api_result.get("pairs", []):
        filtered_pairs.append(
            {item: pair[item] for item in pair.keys() if item in output_include})

    result = {
        "cursor": api_result.get("cursor"),
        "pageSize": api_result.get("pageSize"),
        "page": api_result.get("page"),
        "pairs": filtered_pairs
    }

    return result


@tool
@handle_exceptions
def get_solana_token_swaps(token_address: str, network: str = "mainnet", output_include: list[str] = None,
                           limit: int = 100, cursor: str = "", from_date: str = None, to_date: str = None,
                           order: str = "DESC", transaction_types: str = "buy,sell") -> dict:
    """
    Get all swap related transactions (buy, sell) for a specific Solana token address.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        limit (int): The number of results per page (default: 100, max: 100)
        cursor (str): The cursor returned in the previous response (for pagination)
        from_date (str): Starting date in format accepted by momentjs
        to_date (str): Ending date in format accepted by momentjs
        order (str): The order of results, "ASC" or "DESC" (default: "DESC")
        transaction_types (str): Transaction types to fetch, comma-separated values from "buy", "sell" (default: "buy,sell")

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - page: The current page number
            - pageSize: Number of results per page
            - cursor: The pagination cursor for the next set of results
            - result: List of swap transactions with details like:
              - transactionHash: Transaction signature
              - transactionType: Type of transaction (buy, sell)
              - blockTimestamp: Timestamp of the block
              - walletAddress: Wallet that made the transaction
              - baseToken/quoteToken: Information about traded tokens
              - totalValueUsd: Total value in USD
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/{token_address}/swaps"

    params = {}
    if limit:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor
    if from_date:
        params["fromDate"] = from_date
    if to_date:
        params["toDate"] = to_date
    if order:
        params["order"] = order
    if transaction_types:
        params["transactionTypes"] = transaction_types

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token swaps. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "page": api_result.get("page"),
        "pageSize": api_result.get("pageSize"),
        "cursor": api_result.get("cursor"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_wallet_swaps(wallet_address: str, network: str = "mainnet", output_include: list[str] = None,
                            limit: int = 100, cursor: str = "", from_date: str = None, to_date: str = None,
                            order: str = "DESC", transaction_types: str = "buy,sell", token_address: str = None) -> dict:
    """
    Get all swap related transactions (buy, sell) for a specific Solana wallet address.

    Args:
        wallet_address (str): The wallet address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        limit (int): The number of results per page (default: 100, max: 100)
        cursor (str): The cursor returned in the previous response (for pagination)
        from_date (str): Starting date in format accepted by momentjs
        to_date (str): Ending date in format accepted by momentjs
        order (str): The order of results, "ASC" or "DESC" (default: "DESC")
        transaction_types (str): Transaction types to fetch, comma-separated values from "buy", "sell" (default: "buy,sell")
        token_address (str): Optional token address to filter swaps by

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - page: The current page number
            - pageSize: Number of results per page 
            - cursor: The pagination cursor for the next set of results
            - result: List of swap transactions with details including:
              - transactionHash: Transaction signature
              - transactionType: Type of transaction (buy, sell)
              - blockTimestamp: Timestamp of the block
              - bought/sold: Information about tokens bought and sold
              - totalValueUsd: Total value in USD
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/account/{network}/{wallet_address}/swaps"

    params = {}
    if limit:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor
    if from_date:
        params["fromDate"] = from_date
    if to_date:
        params["toDate"] = to_date
    if order:
        params["order"] = order
    if transaction_types:
        params["transactionTypes"] = transaction_types
    if token_address:
        params["tokenAddress"] = token_address

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana wallet swaps. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "page": api_result.get("page"),
        "pageSize": api_result.get("pageSize"),
        "cursor": api_result.get("cursor"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_pair_stats(pair_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get statistics for a specific Solana trading pair address.

    Args:
        pair_address (str): The pair address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing comprehensive pair statistics including:
            - tokenAddress: The token address
            - tokenName: The token name
            - tokenSymbol: The token symbol
            - pairAddress: The pair address
            - exchange: The exchange name
            - exchangeAddress: The exchange address
            - currentUsdPrice: The current USD price of the token
            - currentNativePrice: The current native price of the token
            - totalLiquidityUsd: Total liquidity in USD
            - pricePercentChange: Price percent change over different timeframes
            - buys/sells: Transaction counts over different timeframes
            - totalVolume: Trading volume over different timeframes
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/pairs/{pair_address}/stats"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana pair stats. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_pair_swaps(pair_address: str, network: str = "mainnet", output_include: list[str] = None,
                          limit: int = 100, cursor: str = "", from_date: str = None, to_date: str = None,
                          order: str = "DESC", transaction_types: str = "buy,sell,addLiquidity,removeLiquidity") -> dict:
    """
    Get all swap related transactions (buy, sell, add liquidity, remove liquidity) for a specific Solana trading pair.

    Args:
        pair_address (str): The pair address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        limit (int): The number of results per page (default: 100, max: 100)
        cursor (str): The cursor returned in the previous response (for pagination)
        from_date (str): Starting date in format accepted by momentjs
        to_date (str): Ending date in format accepted by momentjs
        order (str): The order of results, "ASC" or "DESC" (default: "DESC")
        transaction_types (str): Transaction types to fetch, comma-separated values from "buy", "sell",
                                "addLiquidity", "removeLiquidity" (default: all)

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - page: The current page number
            - pageSize: Number of results per page
            - cursor: The pagination cursor for the next set of results
            - exchangeName: Name of the exchange
            - exchangeLogo: Logo URL of the exchange
            - exchangeAddress: Address of the exchange
            - pairLabel: Label of the trading pair (e.g., "SOL/USDC")
            - pairAddress: Address of the trading pair
            - baseToken: Base token information
            - quoteToken: Quote token information
            - result: List of swap transactions
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/pairs/{pair_address}/swaps"

    params = {}
    if limit:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor
    if from_date:
        params["fromDate"] = from_date
    if to_date:
        params["toDate"] = to_date
    if order:
        params["order"] = order
    if transaction_types:
        params["transactionTypes"] = transaction_types

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana pair swaps. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "page": api_result.get("page"),
        "pageSize": api_result.get("pageSize"),
        "cursor": api_result.get("cursor"),
        "exchangeName": api_result.get("exchangeName"),
        "exchangeLogo": api_result.get("exchangeLogo"),
        "exchangeAddress": api_result.get("exchangeAddress"),
        "pairLabel": api_result.get("pairLabel"),
        "pairAddress": api_result.get("pairAddress"),
        "baseToken": api_result.get("baseToken"),
        "quoteToken": api_result.get("quoteToken"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_pair_candlesticks(pair_address: str, network: str = "mainnet", output_include: list[str] = None,
                                 from_date: str = None, to_date: str = None, timeframe: str = "1min",
                                 currency: str = "usd", limit: int = 100, cursor: str = "") -> dict:
    """
    Get candlestick (OHLCV) data for a specific Solana trading pair.

    Args:
        pair_address (str): The pair address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        from_date (str): Starting date in format accepted by momentjs (required)
        to_date (str): Ending date in format accepted by momentjs (required)
        timeframe (str): The interval of the candlestick ("1s", "10s", "30s", "1min", "5min", "10min", 
                        "30min", "1h", "4h", "12h", "1d", "1w", "1M")
        currency (str): The currency format ("usd" or "native")
        limit (int): The number of results per page (default: 100, max: 1000)
        cursor (str): The cursor returned in the previous response (for pagination)

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - cursor: The pagination cursor for the next set of results
            - page: Current page number
            - pairAddress: Address of the trading pair
            - tokenAddress: Token address (if applicable)
            - timeframe: The interval of the candlesticks
            - currency: The currency format used
            - result: List of candlesticks data points, each containing:
              - timestamp: Timestamp of the candlestick
              - open: Opening price
              - high: Highest price during the period
              - low: Lowest price during the period
              - close: Closing price
              - volume: Trading volume during the period
              - trades: Number of trades during the period
    """
    check_solana_network_supported(network)

    if not from_date or not to_date:
        raise ValueError("Both from_date and to_date are required")

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/pairs/{pair_address}/ohlcv"

    params = {
        "fromDate": from_date,
        "toDate": to_date,
        "timeframe": timeframe,
        "currency": currency
    }

    if limit:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana pair candlesticks. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "cursor": api_result.get("cursor"),
        "page": api_result.get("page"),
        "pairAddress": api_result.get("pairAddress"),
        "tokenAddress": api_result.get("tokenAddress"),
        "timeframe": api_result.get("timeframe"),
        "currency": api_result.get("currency"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_token_prices_multi(addresses: list[str], network: str = "mainnet", output_include: list[str] = None) -> list:
    """
    Get prices for multiple Solana tokens in a single request.

    Args:
        addresses (list[str]): List of token addresses to get prices for (max 100)
        network (str): The Solana network to use: "mainnet" or "devnet" 
        output_include (list[str]): A list of field names to include in the output

    Returns:
        list[dict[str, Any]]:
            A list of dictionaries containing token price data with keys
            listed in `output_include` if provided.

            Possible fields for each token include:
            - tokenAddress: Token address
            - pairAddress: Pair address for the token
            - nativePrice: Native price information object
            - usdPrice: Current price in USD
            - exchangeAddress: Address of the exchange
            - exchangeName: Name of the exchange
            - logo: Token logo URL
            - name: Token name
            - symbol: Token symbol
    """
    check_solana_network_supported(network)

    if not addresses:
        raise ValueError("At least one token address must be provided")

    if len(addresses) > 100:
        raise ValueError("Maximum of 100 token addresses allowed")

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/prices"

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    data = {
        "addresses": addresses
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code != 200 and response.status_code != 201:
        raise Exception(
            f"Failed to get Solana token prices. Status code: {response.status_code} | {response.text}")

    results = response.json()

    if not output_include:
        return results

    filtered_results = []
    for result in results:
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return filtered_results


@tool
@handle_exceptions
def get_solana_token_holders(token_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get the summary of holders for a given Solana token.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing holder statistics including:
            - totalHolders: Total number of token holders
            - holdersByAcquisition: Breakdown of holders by how they acquired tokens
            - holderChange: Statistics about holder changes over different time periods
            - holderDistribution: Distribution of holders by size categories
            - holderSupply: Token supply statistics for top holder groups
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/holders/{token_address}"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token holders. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_historical_token_holders(token_address: str, network: str = "mainnet",
                                        time_frame: str = "1d", from_date: str = None, to_date: str = None,
                                        cursor: str = "", limit: int = 100, output_include: list[str] = None) -> dict:
    """
    Get token holders overtime for a given Solana token.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        time_frame (str): The interval of the holders data ("1min", "5min", "10min", "30min", "1h", "4h", "12h", "1d", "1w", "1m")
        from_date (str): Starting date in format accepted by momentjs (required)
        to_date (str): Ending date in format accepted by momentjs (required)
        cursor (str): The cursor returned in the previous response (for pagination)
        limit (int): The number of results per page (default: 100)
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - cursor: The pagination cursor for the next set of results
            - page: Current page number
            - result: List of time-based holder statistics including:
              - timestamp: The timestamp for this data point
              - totalHolders: Total number of holders at this timestamp
              - netHolderChange: Net change in holder count 
              - holderPercentChange: Percentage change in holders
              - newHoldersByAcquisition: How new holders acquired tokens
              - holdersIn: New holders categorized by size
              - holdersOut: Lost holders categorized by size
    """
    check_solana_network_supported(network)

    if not from_date or not to_date:
        raise ValueError("Both from_date and to_date are required")

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/holders/{token_address}/historical"

    params = {
        "timeFrame": time_frame,
        "fromDate": from_date,
        "toDate": to_date
    }

    if limit:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana historical token holders. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "cursor": api_result.get("cursor"),
        "page": api_result.get("page"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_token_bonding_status(token_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get the token bonding status for a Solana token.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing bonding status information:
            - mint: Token mint address
            - bondingProgress: The progress of token bonding as a percentage
            - graduatedAt: Timestamp when the token graduated from bonding
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/{token_address}/bonding-status"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token bonding status. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_new_tokens_by_exchange(exchange: str, network: str = "mainnet", output_include: list[str] = None,
                                      cursor: str = "", limit: int = 100) -> dict:
    """
    Get the list of new tokens by given exchange.

    Args:
        exchange (str): The exchange name/address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        cursor (str): The cursor returned in the previous response (for pagination)
        limit (int): The number of results per page (default: 100, max: 100)

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - cursor: The pagination cursor for the next set of results
            - pageSize: Number of results per page
            - page: Current page number
            - result: List of new tokens with details including:
              - tokenAddress: Token address
              - name: Token name
              - symbol: Token symbol
              - logo: Token logo URL
              - decimals: Token decimals
              - priceNative: Price in native currency
              - priceUsd: Price in USD
              - liquidity: Token liquidity
              - fullyDilutedValuation: Fully diluted valuation
              - createdAt: Creation timestamp
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/exchange/{exchange}/new"

    params = {}
    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana new tokens by exchange. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "cursor": api_result.get("cursor"),
        "pageSize": api_result.get("pageSize"),
        "page": api_result.get("page"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_bonding_tokens_by_exchange(exchange: str, network: str = "mainnet", output_include: list[str] = None,
                                          cursor: str = "", limit: int = 100) -> dict:
    """
    Get the list of bonding tokens by given Solana exchange.

    Args:
        exchange (str): The exchange name/address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        cursor (str): The cursor returned in the previous response (for pagination)
        limit (int): The number of results per page (default: 100, max: 100)

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - cursor: The pagination cursor for the next set of results
            - pageSize: Number of results per page
            - page: Current page number
            - result: List of bonding tokens with details including:
              - tokenAddress: Token address
              - name: Token name
              - symbol: Token symbol
              - logo: Token logo URL
              - decimals: Token decimals
              - priceNative: Price in native currency
              - priceUsd: Price in USD
              - liquidity: Token liquidity
              - fullyDilutedValuation: Fully diluted valuation
              - bondingCurveProgress: Percentage progress of bonding curve
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/exchange/{exchange}/bonding"

    params = {}
    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana bonding tokens. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "cursor": api_result.get("cursor"),
        "pageSize": api_result.get("pageSize"),
        "page": api_result.get("page"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_graduated_tokens_by_exchange(exchange: str, network: str = "mainnet", output_include: list[str] = None,
                                            cursor: str = "", limit: int = 100) -> dict:
    """
    Get the list of graduated tokens by given Solana exchange.

    Args:
        exchange (str): The exchange name/address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        cursor (str): The cursor returned in the previous response (for pagination)
        limit (int): The number of results per page (default: 100, max: 100)

    Returns:
        dict[str, Any]:
            A dictionary containing:
            - cursor: The pagination cursor for the next set of results
            - pageSize: Number of results per page
            - page: Current page number
            - result: List of graduated tokens with details including:
              - tokenAddress: Token address
              - name: Token name
              - symbol: Token symbol
              - logo: Token logo URL
              - decimals: Token decimals
              - priceNative: Price in native currency
              - priceUsd: Price in USD
              - liquidity: Token liquidity
              - fullyDilutedValuation: Fully diluted valuation
              - graduatedAt: Timestamp when the token graduated
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/exchange/{exchange}/graduated"

    params = {}
    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana graduated tokens. Status code: {response.status_code} | {response.text}")

    api_result = response.json()

    if not output_include:
        return api_result

    filtered_results = []
    for result in api_result.get("result", []):
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return {
        "cursor": api_result.get("cursor"),
        "pageSize": api_result.get("pageSize"),
        "page": api_result.get("page"),
        "result": filtered_results
    }


@tool
@handle_exceptions
def get_solana_nfts(wallet_address: str, network: str = "mainnet", output_include: list[str] = None,
                    nft_metadata: bool = False, media_items: bool = False) -> dict:
    """
    Get NFTs owned by a specific Solana wallet address.
    
    Args:
        wallet_address (str): Solana wallet address
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        nft_metadata (bool): Whether to include the full NFT metadata (default: False)
        media_items (bool): Whether to include media items (default: False)

    Returns:
        list[dict[str, Any]]:
            A list of NFT dictionaries, each containing:
            - associatedTokenAddress: Token associated address
            - mint: NFT mint address
            - name: NFT name
            - symbol: NFT symbol
            - amount: Raw token amount
            - amountRaw: Raw token amount as a string
            - decimals: Number of decimals
            - totalSupply: Total supply
            - attributes: NFT attributes/traits (if nft_metadata is True)
            - collection: Collection information (if nft_metadata is True)
            - media: Media items (if media_items is True)
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/account/{network}/{wallet_address}/nft"

    params = {
        "nftMetadata": str(nft_metadata).lower(),
        "mediaItems": str(media_items).lower()
    }

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana NFTs. Status code: {response.status_code} | {response.text}")

    results = response.json()

    if not output_include:
        return results

    filtered_results = []
    for result in results:
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return filtered_results


@tool
@handle_exceptions
def get_solana_nft_metadata(nft_address: str, network: str = "mainnet", output_include: list[str] = None,
                            media_items: bool = True) -> dict:
    """
    Get the metadata for a specific Solana NFT by its address.

    Args:
        nft_address (str): The NFT mint address
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        media_items (bool): Whether to include media items (default: True)

    Returns:
        dict[str, Any]:
            A dictionary containing NFT metadata:
            - mint: NFT mint address
            - address: NFT address
            - standard: Token standard (e.g., "metaplex")
            - name: NFT name
            - symbol: NFT symbol
            - description: NFT description
            - imageOriginalUrl: Original image URL
            - externalUrl: External URL
            - metadataOriginalUrl: Original metadata URL
            - totalSupply: Total supply of the NFT
            - metaplex: Metaplex-specific data
            - attributes: List of NFT attributes/traits
            - contract: Contract information
            - collection: Collection information
            - firstCreated: Creation information
            - creators: List of creators
            - properties: NFT properties
            - media: Media items (if media_items is True)
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/nft/{network}/{nft_address}/metadata"

    params = {
        "mediaItems": str(media_items).lower()
    }

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana NFT metadata. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_token_metadata(token_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get the global token metadata for a Solana token.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing token metadata:
            - mint: Token mint address
            - standard: Token standard (usually "spl_token")
            - name: Token name
            - symbol: Token symbol
            - logo: Token logo URL
            - decimals: Number of decimals
            - totalSupply: Total supply as a string
            - totalSupplyFormatted: Formatted total supply
            - fullyDilutedValue: Fully diluted market value
            - metaplex: Metaplex-specific data
            - links: Associated links
            - description: Token description
            - isVerifiedContract: Whether the contract is verified
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/{token_address}/metadata"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token metadata. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_portfolio(wallet_address: str, network: str = "mainnet", output_include: list[str] = None,
                         nft_metadata: bool = False, media_items: bool = False) -> dict:
    """
    Get the complete portfolio (native balance, tokens, and NFTs) for a Solana wallet address.

    Args:
        wallet_address (str): The Solana wallet address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output
        nft_metadata (bool): Whether to include full NFT metadata (default: False)
        media_items (bool): Whether to include media items (default: False)

    Returns:
        dict[str, Any]:
            A dictionary containing the wallet's portfolio:
            - nativeBalance: Native SOL balance information
              - solana: Balance in SOL
              - lamports: Balance in lamports
            - nfts: List of NFTs owned by the wallet
            - tokens: List of tokens owned by the wallet
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/account/{network}/{wallet_address}/portfolio"

    params = {
        "nftMetadata": str(nft_metadata).lower(),
        "mediaItems": str(media_items).lower()
    }

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana portfolio. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_token_price(token_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get the token price (USD and native) for a specific Solana token.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing token price information:
            - tokenAddress: Token address
            - pairAddress: Pair address for the token
            - nativePrice: Native price information object
              - value: Raw native price value
              - decimals: Number of decimals
              - name: Native currency name (e.g., "Solana")
              - symbol: Native currency symbol (e.g., "SOL")
            - usdPrice: Current price in USD
            - usdPrice24h: USD price 24 hours ago
            - usdPrice24hrUsdChange: Change in USD over last 24 hours
            - usdPrice24hrPercentChange: Percent change over last 24 hours
            - exchangeAddress: Address of the exchange
            - exchangeName: Name of the exchange
            - logo: Token logo URL
            - name: Token name
            - symbol: Token symbol
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/{token_address}/price"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token price. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_token_balances(wallet_address: str, network: str = "mainnet", output_include: list[str] = None) -> list:
    """
    Get token balances owned by a specific Solana wallet address.

    Args:
        wallet_address (str): The Solana wallet address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        list[dict[str, Any]]:
            A list of token balance dictionaries, each containing:
            - associatedTokenAddress: Token associated address
            - mint: Token mint address
            - name: Token name
            - symbol: Token symbol
            - amount: Token amount (human-readable)
            - amountRaw: Raw token amount as string
            - decimals: Number of token decimals
            - logo: Token logo URL (if available)
            - isVerifiedContract: Whether the contract is verified
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/account/{network}/{wallet_address}/tokens"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token balances. Status code: {response.status_code} | {response.text}")

    results = response.json()

    if not output_include:
        return results

    filtered_results = []
    for result in results:
        filtered_results.append(
            {item: result[item] for item in result.keys() if item in output_include})

    return filtered_results


@tool
@handle_exceptions
def get_solana_native_balance(wallet_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get the native SOL balance for a Solana wallet address.

    Args:
        wallet_address (str): The Solana wallet address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing wallet balance:
            - solana: Balance in SOL
            - lamports: Balance in lamports (raw value)
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/account/{network}/{wallet_address}/balance"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana native balance. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_solana_token_pair_stats(token_address: str, network: str = "mainnet", output_include: list[str] = None) -> dict:
    """
    Get aggregated statistics across all supported pairs of a Solana token.

    Args:
        token_address (str): The token address to query
        network (str): The Solana network to use: "mainnet" or "devnet"
        output_include (list[str]): A list of field names to include in the output

    Returns:
        dict[str, Any]:
            A dictionary containing aggregated statistics:
            - totalLiquidityUsd: Total liquidity across all pairs in USD
            - totalActivePairs: Count of active pairs
            - totalActiveDexes: Count of active exchanges
            - totalSwaps: Swap statistics over different time periods
            - totalVolume: Volume statistics over different time periods
            - totalBuyVolume: Buy volume statistics over different time periods
            - totalSellVolume: Sell volume statistics over different time periods
            - totalBuyers: Unique buyer statistics over different time periods
            - totalSellers: Unique seller statistics over different time periods
    """
    check_solana_network_supported(network)

    api_url = f"{_MORALIS_SOLANA_URL}/token/{network}/{token_address}/pairs/stats"

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Solana token pair stats. Status code: {response.status_code} | {response.text}")

    result = response.json()

    if not output_include:
        return result

    return {item: result[item] for item in result.keys() if item in output_include}
