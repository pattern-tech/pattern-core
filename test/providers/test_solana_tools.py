import json
import requests
import functools

from unittest import mock

from src.agentflow.providers.solana_tools import *
from src.agentflow.utils.shared_tools import log_method

# Test constants
solana_wallet_address = "79hptMY3E6JWvU4dDGQCUT5hDncG4XbyPGyJQXVgUMSd"
solana_token_address = "DKTfwG6EJmEhVyJopLz895BmS9PY8BRNFCNex1Fvp8Je"
solana_nft_address = "7887a9bb00df7cf53080564fa55c2dc720bba44a6ee1b1b9776e6baecdba32c2"
# Example transaction hash
solana_transaction_hash = "4WitbbbytbqsQch7VZfg4SHcgTo6qRw984Q5uEQ5DvdRjg5KCw3VqkBRnggAGZVw6M7kXZsCvdKHq6RPk4YDpAJw"
solana_collection_id = "degods"  # Example collection ID
solana_block_number = 180000000  # Example block number
# Example market address
solana_market_address = "8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6"


@log_method
def test_account_detail():
    detail = get_account_detail.invoke({
        "address": solana_wallet_address
    })
    assert detail is not None
    assert "success" in detail and detail["success"] is True
    assert "account_detail" in detail

    return detail


@log_method
def test_account_transfer():
    transfers = get_account_transfer.invoke({
        "address": solana_wallet_address,
        "page": 1,
        "page_size": 10,
        "sort_by": "block_time",
        "sort_order": "desc"
    })
    assert transfers is not None
    assert "success" in transfers and transfers["success"] is True
    assert "transfers" in transfers

    return transfers


@log_method
def test_account_defi_activities():
    activities = get_account_defi_activities.invoke({
        "address": solana_wallet_address,
        "page": 1,
        "page_size": 10,
        "sort_by": "block_time",
        "sort_order": "desc"
    })
    assert activities is not None
    assert "success" in activities and activities["success"] is True
    assert "defi_activities" in activities

    return activities


@log_method
def test_account_balance_change():
    changes = get_account_balance_change.invoke({
        "address": solana_wallet_address,
        "page": 1,
        "page_size": 10,
        "sort_by": "block_time",
        "sort_order": "desc"
    })
    assert changes is not None
    assert "success" in changes and changes["success"] is True
    assert "balance_changes" in changes

    return changes


@log_method
def test_account_transactions():
    transactions = get_account_transactions.invoke({
        "address": solana_wallet_address,
        "limit": 10
    })
    assert transactions is not None
    assert "success" in transactions and transactions["success"] is True
    assert "transactions" in transactions

    return transactions


@log_method
def test_account_portfolio():
    portfolio = get_account_portfolio.invoke({
        "address": solana_wallet_address
    })
    assert portfolio is not None
    assert "success" in portfolio and portfolio["success"] is True
    assert "portfolio" in portfolio

    return portfolio


@log_method
def test_account_token_accounts():
    token_accounts = get_account_token_accounts.invoke({
        "address": solana_wallet_address,
        "type": "token",
        "page": 1,
        "page_size": 10
    })
    assert token_accounts is not None
    assert "success" in token_accounts and token_accounts["success"] is True
    assert "token_accounts" in token_accounts

    return token_accounts


@log_method
def test_account_stake():
    stake = get_account_stake.invoke({
        "address": solana_wallet_address,
        "page": 1,
        "page_size": 10
    })
    assert stake is not None
    assert "success" in stake and stake["success"] is True
    assert "stake_accounts" in stake

    return stake


@log_method
def test_account_metadata():
    metadata = get_account_metadata.invoke({
        "address": solana_wallet_address
    })
    assert metadata is not None
    assert "success" in metadata and metadata["success"] is True
    assert "metadata" in metadata

    return metadata


@log_method
def test_account_leaderboard():
    leaderboard = get_account_leaderboard.invoke({
        "sort_by": "total_values",
        "sort_order": "desc",
        "page": 1,
        "page_size": 10
    })
    assert leaderboard is not None
    assert "success" in leaderboard and leaderboard["success"] is True
    assert "leaderboard" in leaderboard

    return leaderboard


@log_method
def test_token_transfer():
    transfers = get_token_transfer.invoke({
        "address": solana_token_address,
        "page": 1,
        "page_size": 10,
        "sort_by": "block_time",
        "sort_order": "desc"
    })
    assert transfers is not None
    assert "success" in transfers and transfers["success"] is True
    assert "token_transfers" in transfers

    return transfers


@log_method
def test_token_defi_activities():
    activities = get_token_defi_activities.invoke({
        "address": solana_token_address,
        "page": 1,
        "page_size": 10,
        "sort_by": "block_time",
        "sort_order": "desc"
    })
    assert activities is not None
    assert "success" in activities and activities["success"] is True
    assert "token_defi_activities" in activities

    return activities


@log_method
def test_token_markets():
    markets = get_token_markets.invoke({
        "token": [solana_token_address],
        "page": 1,
        "page_size": 10
    })
    print(markets)
    assert markets is not None
    assert "success" in markets and markets["success"] is True
    assert "token_markets" in markets

    return markets


@log_method
def test_token_meta():
    meta = get_token_meta.invoke({
        "address": solana_token_address
    })
    assert meta is not None
    assert "success" in meta and meta["success"] is True
    assert "token_metadata" in meta

    return meta


@log_method
def test_token_meta_multi():
    meta_multi = get_token_meta_multi.invoke({
        "address": [solana_token_address]
    })
    assert meta_multi is not None
    assert "success" in meta_multi and meta_multi["success"] is True
    assert "tokens_metadata" in meta_multi

    return meta_multi


@log_method
def test_token_price():
    price = get_token_price.invoke({
        "address": solana_token_address
    })
    assert price is not None
    assert "success" in price and price["success"] is True
    assert "token_price" in price

    return price


@log_method
def test_token_price_multi():
    price_multi = get_token_price_multi.invoke({
        "address": [solana_token_address]
    })
    assert price_multi is not None
    assert "success" in price_multi and price_multi["success"] is True
    assert "tokens_price" in price_multi

    return price_multi


@log_method
def test_token_holders():
    holders = get_token_holders.invoke({
        "address": solana_token_address,
        "page": 1,
        "page_size": 10
    })
    assert holders is not None
    assert "success" in holders and holders["success"] is True
    assert "token_holders" in holders

    return holders


@log_method
def test_token_list():
    token_list = get_token_list.invoke({
        "sort_by": "market_cap",
        "sort_order": "desc",
        "page": 1,
        "page_size": 10
    })
    assert token_list is not None
    assert "success" in token_list and token_list["success"] is True
    assert "token_list" in token_list

    return token_list


@log_method
def test_token_top():
    top_tokens = get_token_top.invoke({})
    assert top_tokens is not None
    assert "success" in top_tokens and top_tokens["success"] is True
    assert "top_tokens" in top_tokens

    return top_tokens


@log_method
def test_token_trending():
    trending = get_token_trending.invoke({
        "limit": 10
    })
    assert trending is not None
    assert "success" in trending and trending["success"] is True
    assert "trending_tokens" in trending

    return trending


@log_method
def test_new_nft():
    new_nfts = get_new_nft.invoke({
        "filter": "created_time",
        "page": 1,
        "page_size": 12
    })
    assert new_nfts is not None
    assert "success" in new_nfts and new_nfts["success"] is True
    assert "new_nfts" in new_nfts

    return new_nfts


@log_method
def test_nft_activities():
    activities = get_nft_activities.invoke({
        "page": 1,
        "page_size": 10
    })
    assert activities is not None
    assert "success" in activities and activities["success"] is True
    assert "nft_activities" in activities

    return activities


@log_method
def test_nft_collection_lists():
    collections = get_nft_collection_lists.invoke({
        "range_days": 1,
        "sort_order": "desc",
        "sort_by": "volumes",
        "page": 1,
        "page_size": 10
    })
    assert collections is not None
    assert "success" in collections and collections["success"] is True
    assert "nft_collections" in collections

    return collections


@log_method
def test_nft_collection_items():
    items = get_nft_collection_items.invoke({
        "collection": solana_collection_id,
        "sort_by": "last_trade",
        "page": 1,
        "page_size": 12
    })
    assert items is not None
    assert "success" in items and items["success"] is True
    assert "collection_items" in items

    return items


@log_method
def test_transaction_last():
    last_txs = get_transaction_last.invoke({
        "limit": 10,
        "filter": "exceptVote"
    })
    assert last_txs is not None
    assert "success" in last_txs and last_txs["success"] is True
    assert "latest_transactions" in last_txs

    return last_txs


@log_method
def test_transaction_detail():
    detail = get_transaction_detail.invoke({
        "tx": solana_transaction_hash
    })
    assert detail is not None
    assert "success" in detail and detail["success"] is True
    assert "transaction_detail" in detail

    return detail


@log_method
def test_transaction_actions():
    actions = get_transaction_actions.invoke({
        "tx": solana_transaction_hash
    })
    assert actions is not None
    assert "success" in actions and actions["success"] is True
    assert "transaction_actions" in actions

    return actions


@log_method
def test_block_last():
    last_blocks = get_block_last.invoke({
        "limit": 10
    })
    assert last_blocks is not None
    assert "success" in last_blocks and last_blocks["success"] is True
    assert "latest_blocks" in last_blocks

    return last_blocks


@log_method
def test_block_transactions():
    block_txs = get_block_transactions.invoke({
        "block": solana_block_number,
        "page": 1,
        "page_size": 10
    })
    assert block_txs is not None
    assert "success" in block_txs and block_txs["success"] is True
    assert "block_transactions" in block_txs

    return block_txs


@log_method
def test_block_detail():
    block_detail = get_block_detail.invoke({
        "block": solana_block_number
    })
    assert block_detail is not None
    assert "success" in block_detail and block_detail["success"] is True
    assert "block_detail" in block_detail

    return block_detail


@log_method
def test_market_list():
    markets = get_market_list.invoke({
        "page": 1,
        "page_size": 10,
        "sort_by": "created_time",
        "sort_order": "desc"
    })
    assert markets is not None
    assert "success" in markets and markets["success"] is True
    assert "market_list" in markets

    return markets


@log_method
def test_market_info():
    info = get_market_info.invoke({
        "address": solana_market_address
    })
    assert info is not None
    assert "success" in info and info["success"] is True
    assert "market_info" in info

    return info


@log_method
def test_market_volume():
    volume = get_market_volume.invoke({
        "address": solana_market_address
    })
    assert volume is not None
    assert "success" in volume and volume["success"] is True
    assert "market_volume" in volume

    return volume


@log_method
def test_program_list():
    programs = get_program_list.invoke({
        "sort_by": "num_txs",
        "sort_order": "desc",
        "page": 1,
        "page_size": 10
    })
    assert programs is not None
    assert "success" in programs and programs["success"] is True
    assert "program_list" in programs

    return programs


if __name__ == "__main__":
    # Account endpoint tests
    # test_account_detail()
    # test_account_transfer()
    # test_account_defi_activities()
    # test_account_balance_change()
    # test_account_transactions()
    # test_account_portfolio()
    # test_account_token_accounts()
    # test_account_stake()
    # test_account_metadata()
    # test_account_leaderboard()

    # Token endpoint tests
    # test_token_transfer()
    # test_token_defi_activities()
    # test_token_markets()
    # test_token_meta()
    # test_token_meta_multi()
    # test_token_price()
    # test_token_price_multi()
    # test_token_holders()
    # test_token_list()
    # test_token_top()
    # test_token_trending()

    # NFT endpoint tests
    # test_new_nft()
    # test_nft_activities()
    # test_nft_collection_lists()
    # test_nft_collection_items()

    # Transaction endpoint tests
    # test_transaction_last()
    # test_transaction_detail()
    # test_transaction_actions()

    # Block endpoint tests
    test_block_last()
    test_block_transactions()
    test_block_detail()

    # Market endpoint tests
    test_market_list()
    test_market_info()
    test_market_volume()

    # Program endpoint tests
    test_program_list()
