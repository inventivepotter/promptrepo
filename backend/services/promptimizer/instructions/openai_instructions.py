"""
OpenAI-specific prompt engineering best practices.

Based on official OpenAI documentation:
- https://platform.openai.com/docs/guides/prompt-engineering
- https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
- https://cookbook.openai.com/examples/gpt4-1_prompting_guide
"""

OPENAI_INSTRUCTIONS = """
## OpenAI Best Practices for System Prompts

When crafting prompts for OpenAI models (GPT-4, GPT-4o, GPT-4.1, GPT-5, etc.):

### 1. Be Precise and Explicit
- Use specific, unambiguous language
- Provide concrete examples when possible
- GPT-4.1+ follows instructions more literally and precisely
- State exactly what you want, not what you don't want

### 2. Structure for Clarity
- Use numbered lists or bullet points for multiple instructions
- Separate distinct instructions clearly with line breaks
- Define input/output formats explicitly
- Use delimiters (```, ###, ---) to separate different sections

### 3. Context and Role Definition
- Start with a clear role definition: "You are a [role] that [purpose]"
- Provide relevant context upfront before giving instructions
- Specify the task scope and any limitations
- Define the persona's expertise level and communication style

### 4. For Reasoning Models (GPT-4.5, GPT-5)
- Give high-level guidance rather than step-by-step micromanagement
- Trust the model to work out implementation details
- Focus on describing the desired outcome
- Avoid over-specifying intermediate steps

### 5. Output Format Control
- Specify desired format explicitly (JSON, markdown, plain text)
- Provide output examples when format is important
- Use JSON mode when structured output is needed
- Define response length expectations (brief, detailed, comprehensive)

### 6. Tool Use and Agents
- Define the agent's role clearly
- Enforce structured tool use with examples
- Require validation and testing steps for code generation
- Describe tool capabilities and when to use them

### 7. Iterative Refinement
- Start simple, then add complexity
- Test edge cases and refine instructions
- Use system prompts for persistent behavior
- Keep instructions focused on one primary task
"""
