# Llama Stack Starter Project

This project demonstrates various capabilities of the Llama Stack, including RAG (Retrieval-Augmented Generation), web search, and Wolfram Alpha integration. It serves as a practical implementation guide for using the Llama Stack framework.

For more detailed documentation, please refer to:
- [Llama Stack Official Documentation](https://llama-stack.readthedocs.io/en/latest/getting_started/index.html)
- [Llama Stack Client Python Repository](https://github.com/meta-llama/llama-stack-client-python)

## Prerequisites
- Ollama
- Podman
- Python 3.10+ (Tested with Python 3.10)
- Conda (recommended)

## Project Structure
```
.
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── README.md              # This documentation
├── example_rag.py         # RAG implementation example
├── example_python_sdk.py  # Basic Python SDK usage example
├── tool_websearch_clean.py # Web search agent implementation
├── tool_wolframAlpha.py   # Wolfram Alpha integration example
└── documents/             # Directory for RAG documents
```

## Environment Variables
The following environment variables are required in your `.env` file:
```bash
INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"  # or "meta-llama/Llama-3.1-8B-Instruct"
LLAMA_STACK_PORT=8321
LLAMA_STACK_ENDPOINT="http://localhost:8321"  # or your custom endpoint
TAVILY_SEARCH_API_KEY="your_tavily_api_key"   # Required for web search
WOLFRAM_ALPHA_API_KEY="your_wolfram_api_key"  # Required for Wolfram Alpha integration
```

## Setup Instructions

### 1. Environment Setup
1. Create a new conda environment:
```bash
yes | conda create -n stack-client python=3.10
conda activate stack-client
```

2. Install required packages:
```bash
pip install llama-stack-client
pip install python-dotenv
```

3. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 2. Start Ollama
Run one of the following commands:
```bash
ollama run llama3.2:3b-instruct-fp16 --keepalive 60m
# or
ollama run llama3.1:8b-instruct-fp16 --keepalive 60m
```

### 3. Start Llama Stack Server
1. Set environment variables:
```bash
export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"  # or "meta-llama/Llama-3.1-8B-Instruct"
export LLAMA_STACK_PORT=8321
mkdir -p ~/.llama
```

2. Pull the latest Ollama distribution:
```bash
podman pull docker.io/llamastack/distribution-ollama
```

3. Run the Ollama distribution:
```bash
podman run --privileged -it \
  -p ${LLAMA_STACK_PORT}:${LLAMA_STACK_PORT} \
  -v ~/.llama:/root/.llama \
  --env INFERENCE_MODEL=${INFERENCE_MODEL} \
  --env OLLAMA_URL=http://host.docker.internal:11434 \
  llamastack/distribution-ollama \
  --port ${LLAMA_STACK_PORT}
```

> **Note:** You can add API keys to the podman run command:
```bash
podman run --privileged -it \
  -p ${LLAMA_STACK_PORT}:${LLAMA_STACK_PORT} \
  -v ~/.llama:/root/.llama \
  --env INFERENCE_MODEL=${INFERENCE_MODEL} \
  --env OLLAMA_URL=http://host.docker.internal:11434 \
  --env TAVILY_SEARCH_API_KEY=${TAVILY_SEARCH_API_KEY} \
  --env WOLFRAM_ALPHA_API_KEY=${WOLFRAM_ALPHA_API_KEY} \
  llamastack/distribution-ollama \
  --port ${LLAMA_STACK_PORT}
```

> **Alternative Method:** You can also run Llama Stack using the following command:
```bash
llama stack run --image-type conda ~/vscode/llama-stack/llama_stack/templates/ollama/run.yaml
```

### 4. Configure Llama Stack Client
```bash
llama-stack-client configure --endpoint ${LLAMA_STACK_ENDPOINT}
```
Expected output:
```
> Enter the API key (leave empty if no key is needed):
Done! You can now use the Llama Stack Client CLI with endpoint http://localhost:8321
```

Next, verify the configuration by listing available models:
```bash
llama-stack-client models list
```
You should see a list of available models.

Test the configuration with a simple message:
```bash
llama-stack-client \
  inference chat-completion \
  --message "hello, what model are you?"
```
You should see the LLM's response to your message.

## Available Examples

### 1. Basic Python SDK Example
```bash
python example_python_sdk.py
```
This demonstrates basic interaction with the Llama Stack using the Python SDK.

### 2. RAG Implementation
```bash
python example_rag.py
```
This example shows how to implement Retrieval-Augmented Generation using the Llama Stack.

### 3. Web Search Agent
```bash
python tool_websearch_clean.py
```
A web search agent implementation that uses Tavily Search API to fetch current information.

### 4. Wolfram Alpha Integration
```bash
python tool_wolframAlpha.py
```
An example of integrating Wolfram Alpha for mathematical computations and data analysis.

## Additional Notes
- Make sure to have the required API keys in your `.env` file:
  - `TAVILY_SEARCH_API_KEY` for web search functionality
  - `WOLFRAM_ALPHA_API_KEY` for Wolfram Alpha integration
- The project uses environment variables for configuration, which can be set in the `.env` file
- For the latest Ollama distribution, check: https://hub.docker.com/r/llamastack/distribution-ollama
- The code has been tested with llama-stack-client version 0.2.1
- To update llama-stack-client to the latest version:
  ```bash
  pip install --upgrade llama-stack-client
  ```
- You can check your current llama-stack-client version with:
  ```bash
  pip show llama-stack-client
  ```
- The test directory contains additional examples and test cases for reference
