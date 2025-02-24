from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from termcolor import cprint
import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the environment variables
inference_model = os.getenv("INFERENCE_MODEL")
llama_stack_port = os.getenv("LLAMA_STACK_PORT")
ollama_url = os.getenv("OLLAMA_URL")
wolfram_api_key=os.environ["WOLFRAM_ALPHA_API_KEY"]

print(f"Model: {inference_model}")
print(f"Llama Stack Port: {llama_stack_port}")
print(f"Ollama URL: {ollama_url}")

def create_http_client():
    from llama_stack_client import LlamaStackClient

    return LlamaStackClient(
        base_url=f"http://localhost:{llama_stack_port}", 
    )

# Initialize the Llama Stack client, choosing between library or HTTP client
client = create_http_client()  

# doc for wolfram_alpha is outdated. https://llama-stack.readthedocs.io/en/latest/building_applications/tools.html
# here is new example of using wolfram_alpha tool based on some hints from PR: https://github.com/meta-llama/llama-stack/pull/33
agent_config = AgentConfig(
    model=os.getenv("INFERENCE_MODEL"),
    instructions="You are a helpful wolfram_alpha assistant, use wolfram_alpha tool as external source validation.",
    toolgroups=["builtin::wolfram_alpha"],
    wolfram_api_key=wolfram_api_key,  
    input_shields=[],
    output_shields=[],
    enable_session_persistence=False,
)
agent = Agent(client, agent_config)
user_prompts = [
    "Tell me 10 densest elemental metals",
    "solve x^2 + 2x + 1 = 0",
]

session_id = agent.create_session("test-session")
for prompt in user_prompts:
    cprint(f"User> {prompt}", "green")
    response = agent.create_turn(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        session_id=session_id,
    )
    for log in EventLogger().log(response):
        log.print()