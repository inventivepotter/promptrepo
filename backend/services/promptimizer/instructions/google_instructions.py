"""
Google Gemini-specific prompt engineering best practices.

Based on official Google documentation:
- https://ai.google.dev/gemini-api/docs/prompting-strategies
- https://workspace.google.com/learning/content/gemini-prompt-guide
- https://cloud.google.com/gemini-enterprise/resources/prompt-guide
"""

GOOGLE_INSTRUCTIONS = """
## Google Gemini Best Practices for System Prompts

When crafting prompts for Gemini models (Gemini Pro, Gemini Ultra, Gemini 2.x, Gemini 3):

### 1. Be Precise and Direct
- Use clear, concise language
- State your goal clearly without unnecessary elaboration
- Gemini 3 provides direct, efficient answers by default
- Avoid overly persuasive or verbose language

### 2. Consistent Structure
- Use XML-style tags (e.g., <context>, <task>) OR Markdown headings
- Choose one format and use it consistently within a single prompt
- Clear delimiters help separate different parts of the prompt
- Maintain structural consistency throughout

### 3. Parameter Definition
- Explicitly explain any ambiguous terms or parameters
- Define what success looks like for the task
- Specify constraints and boundaries clearly
- Use clear naming conventions for any variables

### 4. Control Output Verbosity
- Gemini 3 defaults to direct and efficient answers
- If you need conversational or detailed responses, explicitly request them
- Specify length expectations when important
- Use "Be thorough" or "Be brief" to control response length

### 5. Few-Shot Examples
- Provide examples to show patterns
- 2-3 examples are usually sufficient
- Don't over-provide examples (can cause overfitting)
- Use examples to show patterns, not anti-patterns

### 6. Multi-Modal Considerations
- Gemini excels at multi-modal tasks
- Provide clear instructions for each modality (text, image, code)
- Specify how different modalities should interact
- Be explicit about what to extract from each input type

### 7. Gemini 3 Specific Tips
- Simplify prompts that worked for Gemini 2.x
- Elaborate prompts often produce verbose, over-explained outputs
- Follow clarity-first design principles
- Use minimal structured output cues

### 8. Chain-of-Thought for Complex Tasks
- Break multi-step reasoning into focused tasks
- Let each Gemini call handle one focused task
- Use code to chain multiple calls together
- Use lower temperature (0.2) for deterministic tasks

### 9. Natural Language
- Write as if speaking to another person
- Avoid jargon unless necessary for the domain
- Make it conversational for iterative refinement
- Fine-tune prompts based on results
"""
