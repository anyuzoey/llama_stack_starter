import asyncio
import os
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.client_tool import client_tool
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from dotenv import load_dotenv

load_dotenv()

@client_tool
def calculator(x: str, y: str, operation: str) -> dict:
    """Simple calculator tool that performs basic math operations.

    :param x: First number to perform operation on
    :param y: Second number to perform operation on
    :param operation: Mathematical operation to perform ('add', 'subtract', 'multiply', 'divide')
    :returns: Dictionary containing success status and result or error message
    """
    try:
        if operation == "add":
            result = float(x) + float(y)
        elif operation == "subtract":
            result = float(x) - float(y)
        elif operation == "multiply":
            result = float(x) * float(y)
        elif operation == "divide":
            if float(y) == 0:
                return {"success": False, "error": "Cannot divide by zero"}
            result = float(x) / float(y)
        else:
            return {"success": False, "error": "Invalid operation"}

        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def run_main():
    client = LlamaStackClient(
        base_url=f"http://localhost:{os.getenv('LLAMA_STACK_PORT')}"
    )
    agent = Agent(
        client, 
        model=os.getenv("INFERENCE_MODEL"),
        instructions="""You are a calculator assistant. Use the calculator tool to perform operations.
        """,
        tools=[calculator],
        )
    session_id = agent.create_session("calc-session")

    prompt = "What is 25 plus 15?"
    print(f"\nUser: {prompt}")

    try:
        response_gen = agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            session_id=session_id,
            stream=False,
        )

        steps = response_gen.steps
        assert len(steps) == 3
        assert steps[0].step_type == "inference"
        assert steps[1].step_type == "tool_execution"
        assert steps[1].tool_calls[0].tool_name == "calculator"
        assert steps[2].step_type == "inference"
        print(response_gen.steps[1].step_type, response_gen.steps[1].tool_calls[0].tool_name)
        print(response_gen.output_message.content)

    except Exception as e:
        raise RuntimeError(f"Error during agent turn: {e}")

if __name__ == "__main__":
    asyncio.run(run_main())