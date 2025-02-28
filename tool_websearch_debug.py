from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from termcolor import cprint
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the environment variables
inference_model = os.getenv("INFERENCE_MODEL")
llama_stack_port = os.getenv("LLAMA_STACK_PORT")
ollama_url = os.getenv("OLLAMA_URL")

print(f"Model: {inference_model}")
print(f"Llama Stack Port: {llama_stack_port}")
print(f"Ollama URL: {ollama_url}")

def create_http_client():
    from llama_stack_client import LlamaStackClient

    return LlamaStackClient(
        base_url=f"http://localhost:{llama_stack_port}", timeout = 6000,
        provider_data = {"tavily_search_api_key": os.environ['TAVILY_SEARCH_API_KEY']}
    )

# Initialize the Llama Stack client, choosing between library or HTTP client
client = create_http_client()  

print(client.toolgroups.list())

# Below is modified from websearch example from https://colab.research.google.com/github/meta-llama/llama-stack/blob/main/docs/getting_started.ipynb
# Found that brave_search as the first websearch tool always been used due to the order in toolgroups. 
agent_config = AgentConfig(
    model=os.getenv("INFERENCE_MODEL"),
    instructions=(
        "You are a highly knowledgeable and helpful web search assistant. "
        "Your primary goal is to provide accurate and reliable information to the user. "
        "Whenever you encounter a query, make sure to use the websearch tools specifically use travil search tool to look up the most current and precise information available. "
        "name the tool called."
    ),
    toolgroups=["builtin::websearch"],
    provider_id="tavily-search",
    input_shields=[],
    output_shields=[],
    enable_session_persistence=False,
)
agent = Agent(client, agent_config)
user_prompts = [
    "Hello",
    "How US performed in the olympics?"
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
        toolgroups=["builtin::websearch"],
    )
    if response is None:
        print("Warning: Received None response from agent.create_turn")
        continue
    else:
        print(f"Response: {response}")

    try:
        for log in EventLogger().log(response):
            if log is None:
                print("Warning: Received None log")
                continue
            log.print()
    except AttributeError as e:
        print(f"Error: {e}")
        print("Response content:")
        for item in response:
            print(item)

# Unregister all vector databases
for item in client.vector_dbs.list():
    print(f"Unregistering vector database: {item.identifier}")
    client.vector_dbs.unregister(vector_db_id=item.identifier)