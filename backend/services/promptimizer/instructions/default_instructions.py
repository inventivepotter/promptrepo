"""
Default prompt engineering best practices for all LLM providers.

These guidelines apply to any LLM and provide a solid foundation
for effective prompt engineering regardless of the specific model.
"""

DEFAULT_INSTRUCTIONS = """
## Universal Best Practices for System Prompts

These guidelines work effectively across all LLM providers:

### 1. Clear Role Definition
- Start with a clear role: "You are a [role] that [purpose]"
- Define expertise level and domain knowledge
- Specify communication style (formal, casual, technical)
- Set boundaries for what the assistant should and shouldn't do

### 2. Structured Instructions
- Use numbered lists for sequential steps
- Use bullet points for non-sequential items
- Separate sections with clear headers or delimiters
- Group related instructions together

### 3. Context First, Then Instructions
- Provide relevant background information upfront
- Set the scene before giving specific tasks
- Include any constraints or limitations early
- Define the scope of the task clearly

### 4. Specific Output Requirements
- Define the expected format (JSON, markdown, plain text, etc.)
- Specify length expectations (brief, detailed, comprehensive)
- Provide examples of desired output when format matters
- List what should and shouldn't be included

### 5. Examples and Demonstrations
- Include 1-3 examples for complex tasks
- Show input-output pairs when format is important
- Examples clarify better than lengthy descriptions
- Place examples after instructions

### 6. Handling Edge Cases
- Specify behavior for unexpected inputs
- Define fallback responses when needed
- Include error handling instructions
- Clarify what to do when information is insufficient

### 7. Iterative Refinement
- Start with simple prompts and add complexity
- Test with various inputs
- Refine based on actual outputs
- Keep instructions focused on the primary task

### 8. Consistency and Tone
- Maintain consistent terminology throughout
- Use the same terms for the same concepts
- Define any domain-specific vocabulary
- Keep the tone appropriate for the use case
"""
