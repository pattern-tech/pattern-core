# Pattern Core API

## Initialization

### Install Requirements

To install the required dependencies, run:

```sh
cp .env.example .env
cp config.json.example config.json
pip install -r requirements.txt
```

Note: Fill up the `.env` file according to your config


Notes:
- Add your own tool services or use existing ones
- Add provided agents (currently : ``ETHER_SCAN, MORALIS, GOLDRUSH``)
- Choose the llm provider

### Running the Application

#### method 1) Locally

Check the services dependency and make sure all services are up with config provided in `.env` file

depend services:
- postgres

##### Run main app
If you have `make` installed on your machine, you can start the application using:

```sh
make watch
```

Otherwise, you can manually run it with:

```sh
python3 -m uvicorn src.main:app --host 0.0.0.0 --reload
```

#### method 2) Docker Compose

If you have docker compose installed, run:

```sh
docker compose -f docker-compose.yaml up
```

By default, the API runs on port `8000`:

```sh
localhost:8000
```

### API Documentation

We support both Swagger and Scalar documentation:

- Swagger: Available at `/docs`
- Scalar: Available at `/api-doc`

## AI Features

### 1. EtherScan Agent

Agent for handling Ethereum blockchain-related queries and tasks.:

- Get the current Unix timestamp
- Convert a natural language date string into a Unix timestamp
- Retrieve the source code of a smart contract
- Retrieve the ABI of a smart contract
- Retrieve the ABI of a specific event from a smart contract
- Fetch events for a given smart contract event within a block range
- Retrieve the latest Ethereum block number
- Convert a Unix timestamp to the nearest Ethereum block number

### 2. Moralis Agent

Agent for handling Ethereum blockchain-related queries and tasks.:

  - Get active chains for a wallet address across all chains
  - Get token balances for a specific wallet address and their prices in USD. (paginated)
  - Get the stats for a wallet address.
  - Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers and contract interactions.
  - Get the contents of a transaction by the given transaction hash.
  - Get ERC20 approvals for one or many wallet addresses and/or contract addresses, ordered by block number in descending order.

### 3. GoldRush Agent

Agent for handling Ethereum blockchain-related queries and tasks.:

- Get activity across all chains for address
- fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address
- Fetch transactions for a given wallet address (paginated)
- Fetch a summary of transactions (earliest and latest) for a given wallet address.
- Fetch a single transaction including its decoded event logs
- Fetch list of approvals across all token contracts categorized by spenders for a wallet’s assets

### 2. Web Search Integration

This feature enables searching the web using online and indexed search engines, including:

- Answering questions that require web search using Tavily and Perplexity
- Retrieving website content along with their links
- Finding similar links