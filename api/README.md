# Pattern Core API

## Initialization

### Install Requirements

To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

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

By default, the API runs on port `8000`.

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