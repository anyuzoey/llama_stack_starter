import asyncio
import os
import random
import time
import csv
import sys
import types
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.client_tool import client_tool
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from dotenv import load_dotenv
from rich.pretty import pprint
import logging
load_dotenv()


""""
# Very simple draft of LlamaStack Max Tool Experiment

## Overview
This script tests how well LlamaStack handles increasing numbers of tools by measuring **tool selection accuracy, execution success, and latency**. 
## Experiment Setup
- **5 Real Tools**: Weather info, word count, string reversal, uppercase conversion, insurance scoring.
- **Fake Tools**: Dynamically generated tools with random outputs (up to 40 additional tools).
- **5 Fixed Queries**: Each mapped to a ground truth tool.
- **Scaling**: Start with 5 tools, increase by 5 up to 45.
- **Metrics Logged**:
  - Exception Rate (how many exception occurs out of 5 queries)
  - Tool Execution Success Rate (how many time tools are actually executed out of 5 queries)
  - Correct Tool Selection Rate  (how many time correct tool is selected out of 5 queries)
  - Average Latency (average time taken to respond 5 queries)

## Limitations
- **Fake tools are highly similar**, making them easy to distinguish from real tools, also no parameter.
- **Only 5 queries**, limiting diversity in tool usage.
- **Model may perform better here** than in real-world scenarios with more diverse tools.

## Next Steps
- Move to a **proper benchmark** with a broader toolset.
- Incorporate **realistic tool diversity** to stress test selection accuracy.
- Compare results across **different model sizes** to assess generalization.

## Run the Experiment
```bash
python faketooltest.py
```
Results are saved in `experiment_results.csv` for analysis.

"""

# Define real tools
@client_tool
def weather_info(loc: str):
    """Fetches the current weather for a given location.
    
    :param loc: The location for which weather information is requested.
    :returns: A dictionary containing success status and the weather result.
    """
    return {"success": True, "result": f"Weather in {loc} is sunny."}

@client_tool
def word_count(text: str):
    """Counts the number of words in the given text.
    
    :param text: The input text to analyze.
    :returns: A dictionary containing success status and the word count.
    """
    return {"success": True, "result": len(text.split())}

@client_tool
def reverse_string(text: str):
    """Reverses the given string.
    
    :param text: The input text to reverse.
    :returns: A dictionary containing success status and the reversed string.
    """
    return {"success": True, "result": text[::-1]}

@client_tool
def uppercase(text: str):
    """Converts the given string to uppercase.
    
    :param text: The input text to convert.
    :returns: A dictionary containing success status and the uppercase text.
    """
    return {"success": True, "result": text.upper()}

@client_tool
def insurance_scorer(text: str):
    """Generates a insurance score between 1 and 100.
    :param text: The input text to eval.
    :returns: A dictionary containing success status and the generated number.
    """
    return {"success": True, "result": random.randint(1, 100)}

# Generate fake tools using `types.FunctionType`
def generate_fake_tools(n):
    tools = []
    
    for i in range(n):
        tool_name = f"tool_{i}_{generate_random_text(2)}"
        tool_doc = f"""Tool {i} performs a unique operation on the input data. {generate_random_text(10)}
        
        :param input_data: The input data for the tool.
        :returns: A dictionary with success status and a unique response.
        """
        
        def fake_tool(input_data: str, tool_id=i):
            responses = [
                f"Tool {tool_id} processed input: {input_data}",
                f"Tool {tool_id} received: {input_data}",
                f"Input {input_data} was handled by tool {tool_id}",
            ]
            return {"success": True, "result": random.choice(responses)}
        
        fake_tool_fn = types.FunctionType(fake_tool.__code__, globals(), tool_name)
        fake_tool_fn.__doc__ = tool_doc
        print(tool_name)
        print(tool_doc[:100])
        fake_tool_fn = client_tool(fake_tool_fn)
        
        tools.append(fake_tool_fn)
    
    return tools

def generate_random_text(length=10):
    words = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "x-ray", "yankee", "zulu"]
    return " ".join(random.choices(words, k=length))

# Define test queries and ground truth tools
queries = [
    ("What is the weather in New York?", weather_info),
    ("How many words are in 'Hello World, this is a test sentence'?", word_count),
    ("Reverse this text: Python Experiment", reverse_string),
    ("Convert this to uppercase: llamastack", uppercase),
    ("Give me an insurance evaluation score", insurance_scorer)
]

def log_results(results, output_dir, inference_model, environment):
    """Logs experiment results into a CSV file and a log file."""
    # Define the filename for the CSV file
    experiment_date = time.strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_dir, f"results_{inference_model}_{environment}_{experiment_date}.csv")
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Tool Count", "Exception Rate", "Tool Execution Rate", "Correct Tool Rate", "Average Latency (s)"])
        writer.writerows(results)
    
async def run_main():
    # inference_model = os.getenv("INFERENCE_MODEL")
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    print(model_id)
    inference_model = model_id.split("/")[1]
    environment = "local" # "nerc" or "local"

    # Setup logging to a file and the console
    output_dir = "experiment_logs"
    os.makedirs(output_dir, exist_ok=True)

    client = LlamaStackClient(
        base_url=f"http://localhost:{os.getenv('LLAMA_STACK_PORT')}" if environment == "local" else os.getenv("LLAMA_STACK_ENDPOINT")
    )
    
    real_tools = [weather_info, word_count, reverse_string, uppercase, insurance_scorer]
    results = []

    for total_tools in range(5,10, 5):  # Increase by 5 up to 50 tools
        tools = real_tools  + generate_fake_tools(total_tools - len(real_tools))
        print(len(tools))
        
        exception_count = 0
        tool_execution_count = 0
        correct_tool_count = 0
        total_latency = 0

        for i, (query, correct_tool) in enumerate(queries):
            agent = Agent(
                client=client,
                model=model_id,
                instructions="""You are an AI tool calling assistant. Must use the correct tool for each query.
                When using the tools:
                1. Extract the relevant number or values from the user's request.
                2. Use the correct tool to perform the operation.
                3. Present the result clearly.
                4. Handle errors gracefully.""",
                tools=tools,
            )
            session_id = agent.create_session(f"tool-experiment-session-{i+1}")
            print(f'session id is {session_id}')
            
            print(f"\nUser: {query}")
            start_time = time.time()
            
            try:
                response = agent.create_turn(
                    messages=[
                        {"role": "user", "content": query}
                    ],
                    session_id=session_id,
                    stream=False,
                )
                end_time = time.time()
                response_time = end_time - start_time
                total_latency += response_time

                print(f"Inference: {response.output_message.content}")

                steps = response.steps
                if len(steps) > 1:
                    tool_executed = any(step.step_type == "tool_execution" for step in steps)
                    correct_tool_used = any(step.tool_calls[0].tool_name == correct_tool.__name__ for step in steps if step.step_type == "tool_execution")
                    if tool_executed:
                        print(f"Executed Tool: {steps[1].tool_calls[0].tool_name}")
                        print(f"Ground Truth Tool: {correct_tool.__name__}")
                    tool_execution_count += tool_executed
                    correct_tool_count += correct_tool_used
                else:
                    print("Error: Not enough steps in response to access step 1.")
                
            except Exception as e:
                print(f"Error processing query: {e}")
                exception_count += 1

            # session_response = client.agents.session.retrieve(
            #     session_id=session_id,
            #     agent_id=agent.agent_id,
            # )
            # pprint(session_response)

        exception_rate = exception_count / len(queries)
        tool_execution_rate = tool_execution_count / len(queries)
        correct_tool_rate = correct_tool_count / len(queries)
        average_latency = total_latency / len(queries)
        
        results.append([total_tools, exception_rate, tool_execution_rate, correct_tool_rate, average_latency])
        print(f"\nTotal Tools: {total_tools}, Exception Rate: {exception_rate:.2%}, Tool Execution Rate: {tool_execution_rate:.2%}, Correct Tool Rate: {correct_tool_rate:.2%}, Avg Latency: {average_latency:.4f}s")
    
    log_results(results, output_dir, inference_model, environment)

if __name__ == "__main__":
    asyncio.run(run_main())
