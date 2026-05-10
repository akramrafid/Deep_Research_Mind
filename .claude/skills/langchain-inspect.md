# langchain-inspect

Inspect and debug LangChain LCEL chains, visualize chain execution, and optimize chain flow.

## When to Use

- Chain not producing expected output
- Want to understand chain execution flow
- Debugging prompt/response between chain components
- Issues with chain.pipe() or | operator
- Checking intermediate outputs from prompts/LLMs
- Optimizing chain performance

## How to Debug

1. Check `agents.py` for chain definitions
2. Look at `writer_chain` and `critic_chain` in agents.py
3. Verify prompt templates in ChatPromptTemplate
4. Add debugging: print chain.invoke() intermediate steps
5. Check for proper output parser usage

## Tools to Use

- Grep: Search for `chain|`, `prompt|`, `Runnable`
- Read: Inspect agents.py for chain composition
- Bash: Test chains directly with Python