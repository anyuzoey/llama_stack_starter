
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.client_tool import client_tool
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.agent_create_params import AgentConfig


client = LlamaStackClient(base_url="http://localhost:8321")

@client_tool
def torchtune(query: str = "torchtune"):
    """
    Answer information about torchtune.

    :param query: The query to use for querying the internet
    :returns: Information about torchtune
    """
    dummy_response = """
            torchtune is a PyTorch library for easily authoring, finetuning and experimenting with LLMs.

            torchtune provides:

            PyTorch implementations of popular LLMs from Llama, Gemma, Mistral, Phi, and Qwen model families
            Hackable training recipes for full finetuning, LoRA, QLoRA, DPO, PPO, QAT, knowledge distillation, and more
            Out-of-the-box memory efficiency, performance improvements, and scaling with the latest PyTorch APIs
            YAML configs for easily configuring training, evaluation, quantization or inference recipes
            Built-in support for many popular dataset formats and prompt templates
    """
    return dummy_response

agent_config = AgentConfig(
    model="meta-llama/Llama-3.1-8B-Instruct",
    enable_session_persistence = False,
    instructions = "You are a helpful assistant.",
    tool_choice="auto",
    tool_prompt_format="json",
    )

agent = Agent(client=client,
              agent_config=agent_config,
              client_tools=[torchtune]
              )

session_id = agent.create_session("test")
response = agent.create_turn(
            messages=[{"role":"user","content":"What is torchtune?"}],
            session_id= session_id,
            )

for r in EventLogger().log(response):
    r.print()