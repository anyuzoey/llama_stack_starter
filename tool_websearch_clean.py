from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client import LlamaStackClient
from termcolor import cprint
from dotenv import load_dotenv
import os
load_dotenv()

inference_model = os.getenv("INFERENCE_MODEL")
tavily_search_api_key = os.getenv("TAVILY_SEARCH_API_KEY")
endpoint = os.getenv("LLAMA_STACK_ENDPOINT")
port = os.getenv("LLAMA_STACK_PORT")
environment = "local" # "nerc" or "local"
print(f"Model: {inference_model}")

client =  LlamaStackClient(
        base_url=f"http://localhost:{port}" if environment=="local" else endpoint,
        provider_data = {"tavily_search_api_key": tavily_search_api_key}
)

agent = Agent(
    client, 
    model=inference_model,
    instructions=(
        "You are a highly knowledgeable and helpful web search assistant. "
        "Your primary goal is to provide accurate and reliable information to the user. "
        "Whenever you encounter a query, make sure to use the websearch tools specifically use travil search tool to look up the most current and precise information available. "
        "name the tool called."
    ),
    tools=["builtin::websearch"],
    sampling_params={"max_tokens":4096}
)

user_prompts = [
    "How did the USA perform in the last Olympics?",
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
