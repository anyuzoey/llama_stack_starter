# Max Tool Per Agent Experiment

This directory contains my ongoing experiments exploring the limits of how many tools can be effectively passed into Llamastack agents. particularly focusing on how model behavior changes as the number and complexity of tools increases.

## 🔍 Experiment Overview

The core goal is to evaluate **how many tools a model can handle** before its tool selection performance deteriorates. I start by focusing on LLaMA 3B and 8B models (served locally via Ollama), with plans to scale to larger models once the benchmark script is stabilized.

### What We're Testing

- **Tool count vs. performance:** How does increasing the number of tools impact exception rate, execution accuracy, and latency?
- **Effect of token length:** Extending tool descriptions (docstrings) decreases max usable tool count—indicating token budget as a key constraint.
- ** (Guess) Model memory/attention limits:** Evidence suggests models may prioritize recent tool definitions or fail to recall earlier tools past a certain input size.

## 💡 Key Insights So Far
- (update 26 Mar) rule out temperature. 
- (update 24 Mar), 3B model last week consistently give 24 max tool. but this week for v0.1.8, it give 11, 18, 23 max tool for 3 different run. suspect temperature related param were changed for 3B model. 8b model to be tested if it follow same change.
- LLaMA-8B can handle around **21 tools** before misidentifying the correct one.
- **Extending tool descriptions** reduced that number to **18**, suggesting performance is bound by docstring.
- **Extending tool name** reduced that number further to **17**, suggesting performance is bound by tool name.
- **Extending tool return message** does not affect.
- Models may either:
  - Prioritize **later tools** in prompt context (due to recency bias).
  - Or, after exceeding a threshold, **fail to abstract and match** any tools, even among the first few.
- Even when inference still returns a response, the selected tool may be incorrect or invalid.
- **Local vs. cluster-hosted models** (e.g., on NERC) behave differently—even for identical 3B models—likely due to variations in runtime or configuration (e.g., token limit in VLLM's `run.yaml`).

## 📊 Sample Results

For LLaMA-8B Instruct model (log file: `results_Llama-3.1-8B-Instruct_local_20250319_195333.csv`):

| Tool Count | Exception Rate | Execution Rate | Correct Tool Rate | Avg. Latency (s) |
|------------|----------------|----------------|--------------------|------------------|
| 5          | 0.0            | 1.0            | 1.0                | 7.17             |
| 6          | 0.0            | 1.0            | 1.0                | 5.71             |
| 7          | 0.0            | 1.0            | 1.0                | 5.77             |
| ...        | ...            | ...            | ...                | ...              |

More results in the `experiment_logs` directory.

## 📁 Structure

- `maxtool.ipynb`: Automates multi-run tool testing.
- `experiment_logs/`: Contains CSV logs for each model run.
- `count_token.ipynb`: try count tool set tokens.
- `README.md`: This document.

## 🧪 Next Steps

- Add token usage tracking to confirm max tool tokens for each model. (its not the token budge for model like max context length, its the max token size that model can call correct tool from a tool set.)
- Draw graphs comparing model size vs. tool capacity vs. tool token budget.
- Expand testing to additional models (e.g., 13B, possibly 70B via cluster).
- Compare local vs. hosted model behavior in a controlled setting.


todos
how many 5 param tools, 10 param tools.
similar tools how that affect performance.

50 tokens sufficient to describe a tool. 