import os
import sys
from termcolor import cprint  # Used for colored terminal output
from llama_stack_client import LlamaStackClient  # Main client for Llama Stack
from llama_stack_client.lib.agents.agent import Agent  # Agent class for AI interactions
from llama_stack_client.lib.agents.event_logger import EventLogger  # Event logging utility
from llama_stack_client.types.agent_create_params import AgentConfig  # Configuration for agent creation
from llama_stack_client.types import Document  # Document type for Llama Stack interactions
import uuid  # For generating unique identifiers

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
        base_url=f"http://localhost:{llama_stack_port}" # return LlamaStackClient(base_url="http://localhost:8321", timeout = 6000)
    )



def create_library_client(template="ollama"):
    """Creates a library-based client for Llama Stack."""
    from llama_stack import LlamaStackAsLibraryClient

    client = LlamaStackAsLibraryClient(template)
    if not client.initialize():
        print("Llama Stack not built properly")
        sys.exit(1)
    return client


# Initialize the Llama Stack client, choosing between library or HTTP client
client = create_http_client()  # Switch to create_library_client() if needed

# Define agent configuration
agent_config = AgentConfig(
    model=os.getenv("INFERENCE_MODEL"),  # Fetch model from environment variable
    instructions="You are a helpful assistant",  # General AI instructions
    
    # Enable tool usage for additional functionalities (e.g., RAG, code execution)
    toolgroups=[
        "builtin::code_interpreter",  # Enables execution of code within the AI
    ],
    
    max_infer_iters=5,  # Maximum inference iterations per response
    
    sampling_params={  # Defines sampling strategy for AI response generation
        "strategy": {"type": "top_p", "temperature": 0.7, "top_p": 0.95},
        "max_tokens": 2048,  # Token limit per response
    },
    enable_session_persistence=True  # Ensures session persistence across interactions
)

# Create an agent instance with the configured settings
agent = Agent(client, agent_config)

# Start a monitored session
session_id = agent.create_session("monitored_session")

# Send a user query to the AI agent
response = agent.create_turn(
    messages=[{"role": "user", "content": "Analyze this code and run it: 2+2"}],
    session_id=session_id,  # Ensure session ID is correctly passed
)

# Monitor and log each execution step
for log in EventLogger().log(response):
    log.print()