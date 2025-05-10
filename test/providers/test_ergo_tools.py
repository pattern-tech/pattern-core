import json
import requests
import functools

from unittest import mock

from src.agentflow.providers.ergo_tools import *
from src.agentflow.utils.shared_tools import log_method

# Test constants
ergo_transaction_id = "a63b95916e2a487c274f83f80a218ac0c6310ffc8c175232ccd150fe7f2ce010"
ergo_script_template_hash = "4b2d8b7beb3eaac8234d9e61792d270898a43934d6a27275e4f3a044609c9f2a"
ergo_box_id = "e56847ed19b3dc6b72828fcfb992fdf7310828cf291221269b7ffc72fd6bda33"
ergo_address = "3WvsT2Gm4EpJC2PrggD6FFTgM3Jhc4YVXob"
ergo_token_id = "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"
ergo_block_id = "5bc035f5ec5076d3f6a498059e41451897cae5a50b9dddf3b3239dbd3ca6ae52"
ergo_min_gix = 1000000
ergo_limit = 10
ergo_query = "ergodex"
ergo_symbol = "SigUSD"
ergo_ergo_tree = "0008cd03b196b978d77488fba3138876a40a40b9a046c2fbb5ecfa13d4ecf8f1eec52aec"
ergo_ergo_tree_template_hash = "1a9c2189c9b895253b244962539c24c174677d106e5665177f9add281f7d58e4"
ergo_last_epochs = 10
ergo_min_height = 1000000
ergo_max_height = 1001000


@log_method
def test_get_transaction():
    transaction = get_transaction.invoke({
        "tx_id": ergo_transaction_id
    })
    assert transaction is not None
    # No guaranteed response structure, just checking if call works

    return transaction


@log_method
def test_get_transactions_by_inputs_script_template_hash():
    transactions = get_transactions_by_inputs_script_template_hash.invoke({
        "hash": ergo_script_template_hash,
        "offset": 0,
        "limit": ergo_limit,
        "sort_direction": "desc"
    })
    assert transactions is not None

    return transactions


@log_method
def test_get_transactions_by_global_index():
    transactions = get_transactions_by_global_index.invoke({
        "min_gix": ergo_min_gix,
        "limit": ergo_limit
    })
    assert transactions is not None

    return transactions


@log_method
def test_get_box():
    box = get_box.invoke({
        "box_id": ergo_box_id
    })
    assert box is not None

    return box


@log_method
def test_get_unspent_boxes_by_last_epochs():
    boxes = get_unspent_boxes_by_last_epochs.invoke({
        "last_epochs": ergo_last_epochs
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_by_global_index():
    boxes = get_unspent_boxes_by_global_index.invoke({
        "min_gix": ergo_min_gix,
        "limit": ergo_limit
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_stream():
    boxes = get_unspent_boxes_stream.invoke({
        "min_height": ergo_min_height,
        "max_height": ergo_max_height
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_boxes_by_ergo_tree_template_hash_stream():
    boxes = get_boxes_by_ergo_tree_template_hash_stream.invoke({
        "hash": ergo_ergo_tree_template_hash,
        "min_height": ergo_min_height,
        "max_height": ergo_max_height
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_by_ergo_tree_template_hash_stream():
    boxes = get_unspent_boxes_by_ergo_tree_template_hash_stream.invoke({
        "hash": ergo_ergo_tree_template_hash,
        "min_height": ergo_min_height,
        "max_height": ergo_max_height
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_by_token_id():
    boxes = get_unspent_boxes_by_token_id.invoke({
        "token_id": ergo_token_id,
        "offset": 0,
        "limit": ergo_limit,
        "sort_direction": "desc"
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_boxes_by_token_id():
    boxes = get_boxes_by_token_id.invoke({
        "token_id": ergo_token_id,
        "offset": 0,
        "limit": ergo_limit
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_boxes_by_ergo_tree():
    boxes = get_boxes_by_ergo_tree.invoke({
        "ergo_tree": ergo_ergo_tree,
        "offset": 0,
        "limit": ergo_limit
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_boxes_by_ergo_tree_template_hash():
    boxes = get_boxes_by_ergo_tree_template_hash.invoke({
        "hash": ergo_ergo_tree_template_hash,
        "offset": 0,
        "limit": ergo_limit
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_by_ergo_tree():
    boxes = get_unspent_boxes_by_ergo_tree.invoke({
        "ergo_tree": ergo_ergo_tree,
        "offset": 0,
        "limit": ergo_limit,
        "sort_direction": "desc"
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_by_ergo_tree_template_hash():
    boxes = get_unspent_boxes_by_ergo_tree_template_hash.invoke({
        "hash": ergo_ergo_tree_template_hash,
        "offset": 0,
        "limit": ergo_limit
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_boxes_by_address():
    boxes = get_boxes_by_address.invoke({
        "address": ergo_address,
        "offset": 0,
        "limit": ergo_limit
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unconfirmed_unspent_boxes_by_address():
    boxes = get_unconfirmed_unspent_boxes_by_address.invoke({
        "address": ergo_address,
        "sort_direction": "desc"
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_unspent_boxes_by_address():
    boxes = get_unspent_boxes_by_address.invoke({
        "address": ergo_address,
        "offset": 0,
        "limit": ergo_limit,
        "sort_direction": "desc"
    })
    assert boxes is not None

    return boxes


@log_method
def test_get_tokens():
    tokens = get_tokens.invoke({
        "offset": 0,
        "limit": ergo_limit,
        "sort_direction": "desc",
        "hide_nfts": False
    })
    assert tokens is not None

    return tokens


@log_method
def test_search_tokens():
    tokens = search_tokens.invoke({
        "query": ergo_query,
        "offset": 0,
        "limit": ergo_limit
    })
    assert tokens is not None

    return tokens


@log_method
def test_get_tokens_by_symbol():
    tokens = get_tokens_by_symbol.invoke({
        "symbol": ergo_symbol
    })
    assert tokens is not None

    return tokens


@log_method
def test_get_token():
    token = get_token.invoke({
        "token_id": ergo_token_id
    })
    assert token is not None

    return token


@log_method
def test_get_assets():
    assets = get_assets.invoke({
        "offset": 0,
        "limit": ergo_limit,
        "sort_direction": "desc",
        "hide_nfts": False
    })
    assert assets is not None

    return assets


@log_method
def test_search_assets_by_token_id():
    assets = search_assets_by_token_id.invoke({
        "query": ergo_token_id[:5],
        "offset": 0,
        "limit": ergo_limit
    })
    assert assets is not None

    return assets


@log_method
def test_get_epochs_params():
    params = get_epochs_params.invoke({})
    assert params is not None

    return params


@log_method
def test_get_address_transactions():
    transactions = get_address_transactions.invoke({
        "address": ergo_address,
        "offset": 0,
        "limit": ergo_limit,
        "concise": False
    })
    assert transactions is not None

    return transactions


@log_method
def test_get_address_balance_confirmed():
    balance = get_address_balance_confirmed.invoke({
        "address": ergo_address
    })
    assert balance is not None

    return balance


@log_method
def test_get_address_balance_total():
    balance = get_address_balance_total.invoke({
        "address": ergo_address
    })
    assert balance is not None

    return balance


@log_method
def test_get_blocks():
    blocks = get_blocks.invoke({
        "offset": 0,
        "limit": ergo_limit
    })
    assert blocks is not None

    return blocks


@log_method
def test_get_block():
    block = get_block.invoke({
        "block_id": ergo_block_id
    })
    assert block is not None

    return block


@log_method
def test_get_block_headers():
    headers = get_block_headers.invoke({
        "offset": 0,
        "limit": ergo_limit
    })
    assert headers is not None

    return headers


@log_method
def test_get_mempool_transactions_by_address():
    transactions = get_mempool_transactions_by_address.invoke({
        "address": ergo_address,
        "offset": 0,
        "limit": ergo_limit
    })
    assert transactions is not None

    return transactions


@log_method
def test_get_mempool_unspent_boxes():
    boxes = get_mempool_unspent_boxes.invoke({})
    assert boxes is not None

    return boxes


@log_method
def test_get_info():
    info = get_info.invoke({})
    assert info is not None

    return info


@log_method
def test_get_network_state():
    state = get_network_state.invoke({})
    assert state is not None

    return state


if __name__ == "__main__":
    # Transaction endpoint tests
    test_get_transaction()
    test_get_transactions_by_inputs_script_template_hash()
    test_get_transactions_by_global_index()

    # Box endpoint tests
    test_get_box()
    test_get_unspent_boxes_by_last_epochs()
    test_get_unspent_boxes_by_global_index()
    test_get_unspent_boxes_stream()
    test_get_boxes_by_ergo_tree_template_hash_stream()
    test_get_unspent_boxes_by_ergo_tree_template_hash_stream()
    test_get_unspent_boxes_by_token_id()
    test_get_boxes_by_token_id()
    test_get_boxes_by_ergo_tree()
    test_get_boxes_by_ergo_tree_template_hash()
    test_get_unspent_boxes_by_ergo_tree()
    test_get_unspent_boxes_by_ergo_tree_template_hash()
    test_get_boxes_by_address()
    test_get_unconfirmed_unspent_boxes_by_address()
    test_get_unspent_boxes_by_address()

    # Token/Asset endpoint tests
    test_get_tokens()
    test_search_tokens()
    test_get_tokens_by_symbol()
    test_get_token()
    test_get_assets()
    test_search_assets_by_token_id()

    # Epoch endpoint tests
    test_get_epochs_params()

    # Address endpoint tests
    test_get_address_transactions()
    test_get_address_balance_confirmed()
    test_get_address_balance_total()

    # Block endpoint tests
    test_get_blocks()
    test_get_block()
    test_get_block_headers()

    # Mempool endpoint tests
    test_get_mempool_transactions_by_address()
    test_get_mempool_unspent_boxes()

    # Info endpoint tests
    test_get_info()
    test_get_network_state()
