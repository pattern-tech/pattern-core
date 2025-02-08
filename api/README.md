# Pattern Core API

## Initialization

### Install Requirements

To install the required dependencies, run:

```sh
cp .env.example .env
pip install -r requirements.txt
```

Note: Fill up the .env file according to your config

Check the services dependency and make sure all services are up with config provided in `.env` file
- postgres
- minio
- qdrant

### Running the Application

#### Locally

If you have `make` installed on your machine, you can start the application using:

```sh
make watch
```

Otherwise, you can manually run it with:

```sh
python3 -m uvicorn src.main:app --host 0.0.0.0 --reload
```

#### Docker Compose

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

### 1. Ethereum Blockchain Queries

This feature allows handling Ethereum blockchain-related queries and tasks, including:

- Retrieving smart contract source code
- Fetching contract ABIs (Application Binary Interface)
- Getting contract events and their details
- Querying contract transactions
- Converting between timestamps and block numbers

### 2. Web Search Integration

This feature enables searching the web using online and indexed search engines, including:

- Answering questions that require web search using Tavily and Perplexity
- Retrieving website content along with their links
- Finding similar links