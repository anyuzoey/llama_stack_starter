# This is my attempt to llama-stack quick start
please follow more detail by "https://llama-stack.readthedocs.io/en/latest/getting_started/index.html"

## Prerequisite
Ollama
Podman

## Steps
### 1. Start Ollama
`ollama run llama3.2:3b-instruct-fp16 --keepalive 60m`
### 2. Start up the Llama Stack server  
open terminal write
``````
export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"
export LLAMA_STACK_PORT=8321
mkdir -p ~/.llama
``````
then start server by run
```
podman run -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.docker.internal:11434
```
### 3. installing the llama stack client cli and sdk
run following
```
yes | conda create -n stack-client python=3.10
conda activate stack-client

pip install llama-stack-client
```
next testing if it is configed properly
```
llama-stack-client configure --endpoint http://localhost:$LLAMA_STACK_PORT
```
expect output
```
> Enter the API key (leave empty if no key is needed):
Done! You can now use the Llama Stack Client CLI with endpoint http://localhost:8321
```
next run `llama-stack-client models list`
expect to see a list of models you have

next test by giving a user message to it, run
```
llama-stack-client \
  inference chat-completion \
  --message "hello, what model are you?"
```
expect to see llm's outputs

### 4. Run the inference example in quick start example.
I slightly modified it with .env file added.
simplely run `python example_python_sdk.py` you will see llama's text output about coding haiku

### 5. Run the first RAG agent example
same, run `python example_rag.py` 
you will see model output about they searched the rag file and give summary about it.

