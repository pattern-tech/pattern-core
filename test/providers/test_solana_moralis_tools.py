import json
import requests
import functools

from unittest import mock

from src.agentflow.providers.solana_moralis_tools import *
from src.agentflow.utils.shared_tools import log_method


solana_wallet_address = "kXB7FfzdrfZpAZEW3TZcp8a8CwQbsowa6BdfAHZ4gVs"
network = "mainnet"
solana_token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC token address
solana_nft_address = "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt"  # Example NFT address
solana_pair_address = "83v8iPyZihDEjDdY8RdZddyZNyUtXngz69Lgo9Kt5d6d" # Example pair address
solana_exchange = "pumpfun"


@log_method
def test_solana_nfts():
    nfts = get_solana_nfts.invoke(
        {"wallet_address": solana_wallet_address,
         "network": network,
         "output_include": ["mint", "collection"],
         "nft_metadata": True, })
    assert nfts is not None
    assert len(nfts) > 0

    return nfts


@log_method
def test_solana_native_balance():
    balance = get_solana_native_balance.invoke(
        {"wallet_address": solana_wallet_address,
         "network": network})

    assert balance is not None
    assert "solana" in balance
    assert "lamports" in balance

    return balance


@log_method
def test_solana_token_balances():
    balances = get_solana_token_balances.invoke(
        {"wallet_address": solana_wallet_address,
         "network": network,
         "output_include": ["mint", "amount", "symbol"]})
    print(balances)
    assert balances is not None


@log_method
def test_solana_portfolio():
    portfolio = get_solana_portfolio.invoke(
        {"wallet_address": solana_wallet_address,
         "network": network,
         "nft_metadata": False})
    assert portfolio is not None
    assert "nativeBalance" in portfolio
    assert "tokens" in portfolio

    return portfolio


@log_method
def test_solana_token_price():
    price = get_solana_token_price.invoke(
        {"token_address": solana_token_address,
         "network": network,
         "output_include": ["usdPrice", "symbol"]})
    print(price)
    assert price is not None
    assert "usdPrice" in price


@log_method
def test_solana_token_metadata():
    metadata = get_solana_token_metadata.invoke(
        {"token_address": solana_token_address,
         "network": network})
    assert metadata is not None
    assert "symbol" in metadata

    return metadata


@log_method
def test_solana_nft_metadata():
    metadata = get_solana_nft_metadata.invoke(
        {"nft_address": solana_nft_address,
         "network": network,
         "media_items": True})
    print(metadata)
    assert metadata is not None


@log_method
def test_solana_token_pairs():
    pairs = get_solana_token_pairs.invoke(
        {"token_address": solana_token_address,
         "network": network,
         "limit": 5,
         "output_include": ["pairAddress", "pairLabel", "exchangeName"]})

    assert pairs is not None
    assert "pairs" in pairs

    return pairs


@log_method
def test_solana_token_swaps():
    swaps = get_solana_token_swaps.invoke(
        {"token_address": solana_token_address,
         "network": network,
         "limit": 5,
         "output_include": ["transactionHash", "transactionType", "totalValueUsd"]})
    assert swaps is not None

    return swaps


@log_method
def test_solana_wallet_swaps():
    swaps = get_solana_wallet_swaps.invoke(
        {"wallet_address": solana_wallet_address,
         "network": network,
         "limit": 5})
    assert swaps is not None

    return swaps


@log_method
def test_solana_pair_stats():
    stats = get_solana_pair_stats.invoke(
        {"pair_address": solana_pair_address,
         "network": network})

    assert stats is not None

    return stats


@log_method
def test_solana_pair_swaps():
    swaps = get_solana_pair_swaps.invoke(
        {"pair_address": solana_pair_address,
         "network": network,
         "limit": 5})
    assert swaps is not None

    return swaps


@log_method
def test_solana_token_pair_stats():
    stats = get_solana_token_pair_stats.invoke(
        {"token_address": solana_token_address,
         "network": network})
    assert stats is not None

    return stats


@log_method
def test_solana_token_holders():
    holders = get_solana_token_holders.invoke(
        {"token_address": solana_token_address,
         "network": network})
    assert holders is not None

    return holders


@log_method
def test_solana_token_prices_multi():
    prices = get_solana_token_prices_multi.invoke(
        {"addresses": [solana_token_address],
         "network": network,
         "output_include": ["usdPrice", "symbol"]})

    assert prices is not None
    assert len(prices) > 0

    return prices


@log_method
def test_solana_new_tokens_by_exchange():
    tokens = get_solana_new_tokens_by_exchange.invoke(
        {"exchange": solana_exchange,
         "network": network,
         "limit": 5})

    assert tokens is not None
    assert "result" in tokens

    return tokens


@log_method
def test_solana_bonding_tokens_by_exchange():
    tokens = get_solana_bonding_tokens_by_exchange.invoke(
        {"exchange": solana_exchange,
         "network": network,
         "limit": 5})

    assert tokens is not None
    assert "result" in tokens

    return tokens


if __name__ == "__main__":
    test_solana_nfts()
    test_solana_native_balance()
    test_solana_token_balances()
    test_solana_portfolio()
    test_solana_token_price()
    test_solana_token_metadata()
    test_solana_nft_metadata()
    test_solana_token_pairs()
    test_solana_token_swaps()
    test_solana_wallet_swaps()
    test_solana_pair_stats()
    test_solana_pair_swaps()
    test_solana_token_pair_stats()
    test_solana_token_holders()
    test_solana_token_prices_multi()
    test_solana_new_tokens_by_exchange()
    test_solana_bonding_tokens_by_exchange()
