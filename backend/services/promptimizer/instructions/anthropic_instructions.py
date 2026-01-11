"""
Anthropic Claude-specific prompt engineering best practices.

Based on official Anthropic documentation:
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices
- https://github.com/anthropics/prompt-eng-interactive-tutorial
- https://www.anthropic.com/engineering/claude-code-best-practices
"""

ANTHROPIC_INSTRUCTIONS = """
## Anthropic Claude Best Practices for System Prompts

When crafting prompts for Claude models (Claude 3.5, Claude 4, Opus, Sonnet, Haiku):

### 1. Be Clear and Explicit
- State instructions directly and clearly
- Claude 4.x models are trained for precise instruction following
- Provide context and motivation for tasks
- Be specific about what you want rather than vague

### 2. Use XML Tags for Structure
- Claude was trained with XML tags in the training data
- Use tags like <example>, <document>, <context>, <instructions>
- Structure complex inputs with clear delimiters
- Separate different types of content with appropriate tags

Example:
```
<context>
Background information here
</context>

<instructions>
Your task instructions here
</instructions>

<example>
Example input and output here
</example>
```

### 3. Think Step by Step
- Encourage reasoning through complex tasks
- Add "Think step by step" for analytical tasks
- Use chain-of-thought prompting for accuracy
- Allow Claude to show its reasoning process

### 4. Prompt Chaining for Complex Tasks
- Break complex tasks into sub-tasks
- Use output from one step as input to next
- Validate intermediate results
- Keep each prompt focused on one objective

### 5. Few-Shot Learning
- Provide 2-3 examples for complex formats
- Show input-output pairs that demonstrate expected behavior
- Examples clarify subtle requirements better than descriptions
- Place examples after instructions but before the actual task

### 6. Output Format Specificity
- Instead of "be concise", specify "Limit response to 2-3 sentences"
- Define exact format expectations
- Use structured formats (JSON, XML) when parsing is needed
- Specify what should and shouldn't be included

### 7. Avoid Overengineering (Claude Opus 4.5)
- Opus tends to create extra files or unnecessary abstractions
- Explicitly request minimal solutions when appropriate
- Add "Keep solutions focused and minimal" for coding tasks
- Avoid words like "think" when extended thinking is disabled (use "consider", "evaluate" instead)

### 8. Persona and Expertise
- Define Claude's role and expertise level clearly
- Specify communication style (formal, casual, technical)
- Set expectations for depth of responses
- Include domain-specific context when relevant
"""
