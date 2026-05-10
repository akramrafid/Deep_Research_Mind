# prompt-tune

Optimize LLM prompts for better output quality, improve search queries, refine writing instructions, and enhance critic feedback.

## When to Use

- Writer output is too short, generic, or off-topic
- Critic gives unhelpful or vague feedback
- Search results are irrelevant to query
- Reader picks wrong URL or extracts poor content
- Want to add specific formatting requirements
- Need to adjust tone or style

## How to Debug

1. Check prompt templates in `agents.py`
2. Review `writer_prompt`, `critic_prompt` in agents.py
3. Look at SearchAgent and ReaderAgent for implicit prompts
4. Test with different temperature settings
5. Analyze LLM output for patterns to address

## Tools to Use

- Grep: Search for `PromptTemplate`, `from_messages`, `system`
- Read: Inspect agents.py for all prompt definitions
- Bash: Test prompts directly with the LLM