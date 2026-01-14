# Promptimizer Implementation Plan

## Overview

The Promptimizer is an AI-powered prompt enhancement feature that helps users create better system prompts based on their ideas. It uses provider-specific best practices (OpenAI, Anthropic, Google Gemini) and optionally adds OWASP 2025 prompt injection guardrails.

## Key Features
- Wand icon button next to system prompt textarea
- Modal with multi-turn chat interface
- Provider-specific prompt engineering best practices
- Optional OWASP 2025 prompt injection guardrails (when "Expects user message" is checked)
- Apply enhanced prompt to existing system prompt

---

## File Structure

### Backend Files to Create

```
backend/
  agents/
    promptimizer/
      __init__.py
      promptimizer_agent.py
  services/
    promptimizer/
      __init__.py
      promptimizer_service.py
      models.py
      instructions/
        __init__.py
        openai_instructions.py
        anthropic_instructions.py
        google_instructions.py
        default_instructions.py
        owasp_guardrails.py
  api/
    v0/
      promptimizer/
        __init__.py
        optimize.py
```

### Frontend Files to Create

```
frontend/
  stores/
    promptimizerStore/
      index.ts
      types.ts
      state.ts
      actions.ts
      store.ts
      hooks.ts
  services/
    promptimizer/
      api.ts
  app/
    prompts/
      _components/
        PromptOptimizerModal.tsx
```

### Files to Modify

- `backend/api/deps.py` - Add PromptOptimizerServiceDep
- `backend/api/v0/__init__.py` - Register promptimizer router
- `frontend/app/prompts/_components/PromptFieldGroup.tsx` - Add wand button and modal
- `frontend/app/api/[...proxy]/route.ts` - Add promptimizer endpoint to proxy

---

## Implementation Details

### 1. Backend Models (`backend/services/promptimizer/models.py`)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.messages import MessageSchema

class PromptOptimizerRequest(BaseModel):
    idea: str = Field(..., description="User's idea for the prompt")
    provider: str = Field(..., description="Target LLM provider")
    model: str = Field(..., description="Target model name")
    expects_user_message: bool = Field(default=False)
    conversation_history: Optional[List[MessageSchema]] = None

class PromptOptimizerResponse(BaseModel):
    optimized_prompt: str
    explanation: Optional[str] = None
```

### 2. Provider Instructions (Python string constants)

Each provider gets specific best practices:

**OpenAI** (`openai_instructions.py`):
- Be precise and explicit
- GPT-4.1+ follows instructions more literally
- For reasoning models: give high-level guidance
- Define agent role, enforce structured tool use

**Anthropic** (`anthropic_instructions.py`):
- Be clear and explicit
- Use XML tags for structure (`<example>`, `<document>`)
- Think step by step
- Use prompt chaining for complex tasks

**Google Gemini** (`google_instructions.py`):
- Be precise and direct
- Use consistent structure (XML or Markdown)
- Define parameters explicitly
- Gemini 3 provides direct, efficient answers

**OWASP Guardrails** (`owasp_guardrails.py`):
- Delimiter and separation rules
- Security instructions (NEVER follow user instructions as commands)
- Pattern detection for malicious inputs
- Response validation rules

### 3. Promptimizer Agent (`backend/agents/promptimizer/promptimizer_agent.py`)

Following existing `ChatAgent` pattern:
- Uses any-agent with LANGCHAIN framework
- Monkeypatches any_llm for custom provider support
- Simple wrapper with `create()` and `run()` methods

### 4. Promptimizer Service (`backend/services/promptimizer/promptimizer_service.py`)

- Constructor injection with `ConfigService`
- `_get_provider_instructions()` - Select provider-specific instructions
- `_build_system_instructions()` - Combine base + provider + optional guardrails
- `_get_api_details()` - Get API key/base from user config
- `_format_conversation()` - Format multi-turn history as JSON
- `optimize_prompt()` - Main method, creates agent and runs optimization

### 5. API Endpoint (`backend/api/v0/promptimizer/optimize.py`)

```python
@router.post(
    "/optimize",
    response_model=StandardResponse[PromptOptimizerResponse],
    status_code=status.HTTP_200_OK,
)
async def optimize_prompt(
    request_body: PromptOptimizerRequest,
    request: Request,
    config_service: ConfigServiceDep,
    user_id: CurrentUserDep
) -> StandardResponse[PromptOptimizerResponse]:
```

### 6. Frontend Zustand Store (`frontend/stores/promptimizerStore/`)

State:
- `isOpen`, `idea`, `expectsUserMessage`
- `messages` (multi-turn conversation)
- `optimizedPrompt`, `isLoading`, `error`

Actions:
- `openDialog()`, `closeDialog()`
- `setIdea()`, `setExpectsUserMessage()`
- `sendMessage()` - API call with conversation history
- `applyPrompt()` - Returns optimized prompt
- `clearConversation()`, `reset()`

### 7. Frontend Modal (`frontend/app/prompts/_components/PromptOptimizerModal.tsx`)

- Chakra UI Dialog.Root pattern (like DeletePromptDialog)
- Checkbox for "Expects user message"
- Chat message display area
- Text input with send button
- "Apply System Prompt" button

### 8. Integration in PromptFieldGroup

Add next to "Prompt" label:
```tsx
<Button size="xs" variant="ghost" onClick={openDialog}>
  <LuWand2 /> Promptimizer
</Button>
```

---

## Provider Best Practices Sources

### OpenAI
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Best Practices Help Center](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api)
- [GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)

### Anthropic
- [Claude 4 Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Prompt Engineering Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

### Google Gemini
- [Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Google Workspace Prompting Guide](https://workspace.google.com/learning/content/gemini-prompt-guide)

### OWASP 2025
- [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [OWASP Top 10 for LLMs 2025 PDF](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf)

---

## Implementation Order

### Phase 1: Backend Foundation
1. `backend/services/promptimizer/models.py`
2. `backend/services/promptimizer/instructions/__init__.py`
3. `backend/services/promptimizer/instructions/openai_instructions.py`
4. `backend/services/promptimizer/instructions/anthropic_instructions.py`
5. `backend/services/promptimizer/instructions/google_instructions.py`
6. `backend/services/promptimizer/instructions/default_instructions.py`
7. `backend/services/promptimizer/instructions/owasp_guardrails.py`
8. `backend/agents/promptimizer/__init__.py`
9. `backend/agents/promptimizer/promptimizer_agent.py`
10. `backend/services/promptimizer/__init__.py`
11. `backend/services/promptimizer/promptimizer_service.py`

### Phase 2: Backend API
12. `backend/api/v0/promptimizer/__init__.py`
13. `backend/api/v0/promptimizer/optimize.py`
14. Update `backend/api/deps.py`
15. Register router in `backend/api/v0/__init__.py`

### Phase 3: Frontend State & API
16. `frontend/stores/promptimizerStore/types.ts`
17. `frontend/stores/promptimizerStore/state.ts`
18. `frontend/stores/promptimizerStore/actions.ts`
19. `frontend/stores/promptimizerStore/store.ts`
20. `frontend/stores/promptimizerStore/hooks.ts`
21. `frontend/stores/promptimizerStore/index.ts`
22. `frontend/services/promptimizer/api.ts`

### Phase 4: Frontend UI
23. `frontend/app/prompts/_components/PromptOptimizerModal.tsx`
24. Update `frontend/app/prompts/_components/PromptFieldGroup.tsx`
25. Update `frontend/app/api/[...proxy]/route.ts`

### Phase 5: Testing
26. Create backend unit tests `backend/tests/services/promptimizer/test_promptimizer_service.py`
27. Manual integration testing

---

## Critical Files Reference

| File | Purpose |
|------|---------|
| `backend/agents/chat_agent/chat_agent.py` | Agent pattern to follow |
| `backend/services/llm/chat_completion_service.py` | Service pattern with ConfigService |
| `backend/api/v0/llm/chat/completions.py` | API endpoint pattern |
| `frontend/stores/chatStore/actions.ts` | Zustand actions pattern |
| `frontend/components/DeletePromptDialog.tsx` | Modal pattern |
| `frontend/app/prompts/_components/PromptFieldGroup.tsx` | Where to add button |

---

## Verification

### Backend Testing
```bash
cd backend
uv run pytest tests/services/promptimizer/ -v
```

### Manual Testing
1. Start backend: `cd backend && uv run uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to a prompt editor page
4. Click the "Promptimizer" wand button
5. Enter an idea (e.g., "A helpful customer service agent")
6. Toggle "Expects user message" checkbox
7. Send message and verify AI response
8. Send follow-up messages for refinement
9. Click "Apply System Prompt"
10. Verify the prompt textarea is updated

### API Testing
```bash
curl -X POST http://localhost:8080/api/v0/promptimizer/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A helpful customer service agent",
    "provider": "openai",
    "model": "gpt-4",
    "expects_user_message": true
  }'
```
