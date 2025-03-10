from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from termcolor import cprint
import os
from llama_stack_client import LlamaStackClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the environment variables
inference_model = os.getenv("INFERENCE_MODEL")
llama_stack_port = os.getenv("LLAMA_STACK_PORT")
ollama_url = os.getenv("OLLAMA_URL")
tavily_search_api_key = os.environ["TAVILY_SEARCH_API_KEY"]
wolfram_api_key=os.environ["WOLFRAM_ALPHA_API_KEY"]


# Initialize the Llama Stack client, choosing between library or HTTP client
client = LlamaStackClient(
        base_url=f"http://localhost:{llama_stack_port}", # return LlamaStackClient(base_url="http://localhost:8321", timeout = 6000)
        provider_data = {"tavily_search_api_key": tavily_search_api_key,
                         "wolfram_alpha_api_key": wolfram_api_key}  # according to https://llama-stack.readthedocs.io/en/latest/building_applications/tools.html
    )  

print(client.toolgroups.list())

# `agent_config` is deprecated. Use inlined parameters instead.
agent = Agent(
    client, 
    model=inference_model,
    instructions="""
    You are a helpful tool calling assistant. 
    There are three builtin tools: websearch, code_interpreter, wolfram_alpha. 
    Select the best tool for each query and execute this query for accurate answer. 
    If there is a error, try another suitable tool.
    """,
    tools=["builtin::websearch",
           "builtin::code_interpreter",
           "builtin::wolfram_alpha"],)
user_prompts = [
    "Hello",
    "Tell me 10 densest elemental metals",
    "solve x^2 + 2x + 1 = 0",
    "Run this code: 2**4 + 8 - 3\nprint(result)",
    "Which teams played in the NBA western conference finals of 2024",
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