from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client import LlamaStackClient
from termcolor import cprint
from dotenv import load_dotenv
import os
load_dotenv()

inference_model = os.getenv("INFERENCE_MODEL")
wolfram_api_key=os.getenv("WOLFRAM_ALPHA_API_KEY")
endpoint = os.getenv("LLAMA_STACK_ENDPOINT")
port = os.getenv("LLAMA_STACK_PORT")
environment = "local" # "nerc" or "local"
print(f"Model: {inference_model}")

client =  LlamaStackClient(
        base_url=f"http://localhost:{port}" if environment=="local" else endpoint,
        provider_data = {"wolfram_alpha_api_key": wolfram_api_key}
)

agent = Agent(
    client,
    model=inference_model,
    instructions="You are a helpful wolfram_alpha assistant, must use builtin::wolfram_alpha tool as external source validation.",
    tools=["builtin::wolfram_alpha"],
)

user_prompts = [
    "solve x^2 + 2x + 1 = 0 using wolfram alpha",
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
