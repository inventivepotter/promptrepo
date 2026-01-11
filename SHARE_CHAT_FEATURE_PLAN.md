# Share Chat Experience Feature Plan

## Overview

This feature enables users to share their chat playground experience with colleagues or publicly via a generated link. The shared view displays an immutable, read-only version of the chat conversation with all metadata (model, token usage, cost, etc.) preserved.

---

## User Stories

1. **As a user**, I want to share my chat session with colleagues so they can see the conversation I had with the AI agent.
2. **As a viewer**, I want to view a shared chat in read-only mode with all the context (model used, token usage, costs) visible.
3. **As a user**, I want to generate a shareable link with a single click from the chat interface.

---

## Technical Design

### 1. Database Schema

#### New Table: `shared_chats`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `share_id` | VARCHAR(32) | Unique short ID for URL (e.g., `abc123xyz`) |
| `title` | VARCHAR(255) | Chat session title |
| `messages` | JSONB | Full messages array serialized as JSON |
| `model_config` | JSONB | Model configuration (provider, model, temperature, etc.) |
| `prompt_meta` | JSONB | Prompt metadata (system prompt, tools, etc.) |
| `total_tokens` | INTEGER | Total tokens used in session |
| `total_cost` | FLOAT | Total cost of session |
| `created_by` | UUID | FK to users table (nullable for anonymous shares) |
| `created_at` | TIMESTAMP | When the share was created |
| `expires_at` | TIMESTAMP | Optional expiration date (nullable for permanent shares) |
| `is_active` | BOOLEAN | Soft delete flag |

**Indexes:**
- `share_id` (UNIQUE) - For fast URL lookups
- `created_by` - For user's shared chats listing
- `created_at` - For sorting

---

### 2. Backend Implementation

#### 2.1 New Pydantic Schemas

**Location:** `backend/schemas/shared_chat.py`

```python
class SharedChatMessage(BaseModel):
    """Message structure for shared chat storage"""
    id: str
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: datetime
    usage: Optional[TokenUsageSchema] = None
    cost: Optional[float] = None
    inference_time_ms: Optional[float] = None
    tool_calls: Optional[List[ToolCallSchema]] = None

class SharedChatModelConfig(BaseModel):
    """Model configuration for shared chat"""
    provider: str
    model: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class CreateSharedChatRequest(BaseModel):
    """Request to create a shared chat"""
    title: str
    messages: List[SharedChatMessage]
    model_config: SharedChatModelConfig
    prompt_meta: Optional[Dict[str, Any]] = None
    total_tokens: int
    total_cost: float

class SharedChatResponse(BaseModel):
    """Response containing shared chat data"""
    id: str
    share_id: str
    title: str
    messages: List[SharedChatMessage]
    model_config: SharedChatModelConfig
    prompt_meta: Optional[Dict[str, Any]] = None
    total_tokens: int
    total_cost: float
    created_at: datetime

class CreateSharedChatResponse(BaseModel):
    """Response after creating a shared chat"""
    share_id: str
    share_url: str
```

#### 2.2 Database Model

**Location:** `backend/models/shared_chat.py`

```python
class SharedChat(Base):
    __tablename__ = "shared_chats"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    share_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    messages: Mapped[dict] = mapped_column(JSONB)
    model_config_data: Mapped[dict] = mapped_column(JSONB)  # Avoiding conflict with Pydantic
    prompt_meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    total_tokens: Mapped[int] = mapped_column(Integer)
    total_cost: Mapped[float] = mapped_column(Float)
    created_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
```

#### 2.3 Repository

**Location:** `backend/repositories/shared_chat_repository.py`

```python
class SharedChatRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, shared_chat: SharedChat) -> SharedChat
    async def get_by_share_id(self, share_id: str) -> Optional[SharedChat]
    async def get_by_user(self, user_id: UUID, limit: int, offset: int) -> List[SharedChat]
    async def delete(self, share_id: str, user_id: UUID) -> bool
```

#### 2.4 Service

**Location:** `backend/services/shared_chat_service.py`

```python
class SharedChatService:
    def __init__(self, repository: SharedChatRepository):
        self.repository = repository

    def generate_share_id(self) -> str:
        """Generate a unique, URL-safe share ID (e.g., nanoid or short UUID)"""

    async def create_shared_chat(
        self,
        request: CreateSharedChatRequest,
        user_id: Optional[UUID]
    ) -> CreateSharedChatResponse

    async def get_shared_chat(self, share_id: str) -> SharedChatResponse

    async def delete_shared_chat(self, share_id: str, user_id: UUID) -> bool
```

#### 2.5 API Endpoints

**Location:** `backend/api/v0/shared_chat/`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v0/shared-chats` | Create a new shared chat | Yes |
| GET | `/api/v0/shared-chats/{share_id}` | Get shared chat by ID | No (public) |
| GET | `/api/v0/shared-chats` | List user's shared chats | Yes |
| DELETE | `/api/v0/shared-chats/{share_id}` | Delete a shared chat | Yes (owner only) |

**Endpoint Details:**

```python
# POST /api/v0/shared-chats
@router.post(
    "",
    response_model=StandardResponse[CreateSharedChatResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create shared chat",
    description="Create a shareable link for a chat session"
)
async def create_shared_chat(
    request: Request,
    body: CreateSharedChatRequest,
    service: SharedChatServiceDep,
    current_user: CurrentUserDep
) -> StandardResponse[CreateSharedChatResponse]:
    ...

# GET /api/v0/shared-chats/{share_id}
@router.get(
    "/{share_id}",
    response_model=StandardResponse[SharedChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Get shared chat",
    description="Retrieve a shared chat by its share ID (public endpoint)"
)
async def get_shared_chat(
    share_id: str,
    service: SharedChatServiceDep
) -> StandardResponse[SharedChatResponse]:
    ...
```

---

### 3. Frontend Implementation

#### 3.1 New API Client

**Location:** `frontend/services/sharedChat/`

```typescript
// types.ts
interface SharedChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: string;
  usage?: TokenUsage;
  cost?: number;
  inferenceTimeMs?: number;
  toolCalls?: ToolCall[];
}

interface SharedChatModelConfig {
  provider: string;
  model: string;
  temperature?: number;
  maxTokens?: number;
}

interface CreateSharedChatRequest {
  title: string;
  messages: SharedChatMessage[];
  modelConfig: SharedChatModelConfig;
  promptMeta?: Record<string, unknown>;
  totalTokens: number;
  totalCost: number;
}

interface SharedChatResponse {
  id: string;
  shareId: string;
  title: string;
  messages: SharedChatMessage[];
  modelConfig: SharedChatModelConfig;
  promptMeta?: Record<string, unknown>;
  totalTokens: number;
  totalCost: number;
  createdAt: string;
}

// api.ts
class SharedChatApi {
  static async createSharedChat(request: CreateSharedChatRequest): Promise<CreateSharedChatResponse>
  static async getSharedChat(shareId: string): Promise<SharedChatResponse>
  static async listSharedChats(): Promise<SharedChatResponse[]>
  static async deleteSharedChat(shareId: string): Promise<void>
}
```

#### 3.2 Chat Store Updates

**Location:** `frontend/stores/chatStore/actions.ts`

Add new action:

```typescript
shareCurrentSession: async () => {
  const { currentSession, totalTokensUsed, totalCost } = get();
  if (!currentSession) return null;

  const response = await SharedChatApi.createSharedChat({
    title: currentSession.title,
    messages: currentSession.messages,
    modelConfig: currentSession.modelConfig,
    totalTokens: totalTokensUsed,
    totalCost: totalCost,
  });

  return response.shareUrl;
}
```

#### 3.3 Share Button Component

**Location:** `frontend/app/prompts/_components/ShareChatButton.tsx`

```typescript
interface ShareChatButtonProps {
  disabled?: boolean;
}

export function ShareChatButton({ disabled }: ShareChatButtonProps) {
  const [isSharing, setIsSharing] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const shareCurrentSession = useChatStore(state => state.shareCurrentSession);

  const handleShare = async () => {
    setIsSharing(true);
    try {
      const url = await shareCurrentSession();
      setShareUrl(url);
      // Show modal or copy to clipboard
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <Button onClick={handleShare} disabled={disabled || isSharing}>
      <ShareIcon /> Share
    </Button>
  );
}
```

#### 3.4 Share Modal Component

**Location:** `frontend/app/prompts/_components/ShareChatModal.tsx`

Features:
- Display generated share URL
- Copy to clipboard button
- Close button
- Success feedback

#### 3.5 Update Chat Header

**Location:** `frontend/app/prompts/_components/ChatSimpleHeader.tsx`

Add ShareChatButton next to the reset button:

```typescript
export function ChatSimpleHeader({ ... }) {
  return (
    <div className="...">
      <ShareChatButton disabled={messages.length === 0} />
      <Button onClick={onReset}>Reset</Button>
      {/* ... */}
    </div>
  );
}
```

#### 3.6 Shared Chat View Page (Public)

**Location:** `frontend/app/shared/[shareId]/page.tsx`

This is a **public page** (no authentication required).

```typescript
interface SharedChatPageProps {
  params: { shareId: string };
}

export default async function SharedChatPage({ params }: SharedChatPageProps) {
  // Server-side fetch of shared chat data
  const sharedChat = await getSharedChat(params.shareId);

  return (
    <div className="shared-chat-container">
      <SharedChatHeader
        title={sharedChat.title}
        modelConfig={sharedChat.modelConfig}
        createdAt={sharedChat.createdAt}
      />
      <SharedChatTokenStats
        totalTokens={sharedChat.totalTokens}
        totalCost={sharedChat.totalCost}
      />
      <SharedChatMessages messages={sharedChat.messages} />
      <SharedChatFooter />
    </div>
  );
}
```

#### 3.7 Shared Chat Components

**Location:** `frontend/app/shared/_components/`

| Component | Description |
|-----------|-------------|
| `SharedChatHeader.tsx` | Displays title, model info, creation date |
| `SharedChatMessages.tsx` | Read-only message list (reuses ChatMessages styling) |
| `SharedChatTokenStats.tsx` | Token and cost summary |
| `SharedChatFooter.tsx` | Branding/attribution footer |

**Key differences from regular chat:**
- No input field
- No reset button
- No edit/regenerate actions
- No template variables section
- All content is immutable/read-only
- Shows "Shared on [date]" indicator

---

### 4. Frontend Proxy Configuration

**Location:** `frontend/next.config.js` (or API route)

Ensure the new endpoint is accessible through the frontend proxy:

```javascript
// Add to existing rewrites
{
  source: '/api/v0/shared-chats/:path*',
  destination: `${BACKEND_URL}/api/v0/shared-chats/:path*`,
}
```

---

### 5. URL Structure

| URL | Description |
|-----|-------------|
| `/shared/{shareId}` | Public shared chat view |

Example: `https://app.example.com/shared/abc123xyz`

---

## Implementation Phases

### Phase 1: Backend Foundation
1. Create database migration for `shared_chats` table
2. Implement `SharedChat` model
3. Implement `SharedChatRepository`
4. Implement `SharedChatService`
5. Create API endpoints
6. Add unit tests for service and repository

### Phase 2: Frontend Share Flow
1. Create SharedChat API client
2. Add `shareCurrentSession` action to chat store
3. Implement ShareChatButton component
4. Implement ShareChatModal component
5. Update ChatSimpleHeader to include share button

### Phase 3: Public Shared View
1. Create `/shared/[shareId]` page route
2. Implement SharedChatHeader component
3. Implement SharedChatMessages component (read-only)
4. Implement SharedChatTokenStats component
5. Implement SharedChatFooter component
6. Configure frontend proxy for shared-chats endpoints

### Phase 4: Polish & Testing
1. Add loading and error states
2. Handle edge cases (expired links, deleted chats)
3. Add E2E tests
4. Add proper SEO meta tags for shared pages

---

## Security Considerations

1. **Share ID Generation**: Use cryptographically secure random IDs (nanoid or UUID) to prevent guessing
2. **Rate Limiting**: Limit share creation to prevent abuse
3. **Content Validation**: Sanitize message content before storage
4. **No PII Exposure**: Shared chats should not expose user IDs or sensitive metadata
5. **Optional Expiration**: Consider adding expiration option for sensitive conversations

---

## Future Enhancements (Out of Scope)

1. Password-protected shares
2. View count analytics
3. Comments/annotations on shared chats
4. Share expiration settings
5. Edit/revoke shared links
6. Organization-wide sharing permissions

---

## File Changes Summary

### New Files

**Backend:**
- `backend/schemas/shared_chat.py`
- `backend/models/shared_chat.py`
- `backend/repositories/shared_chat_repository.py`
- `backend/services/shared_chat_service.py`
- `backend/api/v0/shared_chat/__init__.py`
- `backend/api/v0/shared_chat/router.py`
- `backend/tests/services/test_shared_chat_service.py`
- `backend/tests/api/v0/test_shared_chat.py`
- Alembic migration file

**Frontend:**
- `frontend/services/sharedChat/types.ts`
- `frontend/services/sharedChat/api.ts`
- `frontend/services/sharedChat/index.ts`
- `frontend/app/prompts/_components/ShareChatButton.tsx`
- `frontend/app/prompts/_components/ShareChatModal.tsx`
- `frontend/app/shared/[shareId]/page.tsx`
- `frontend/app/shared/_components/SharedChatHeader.tsx`
- `frontend/app/shared/_components/SharedChatMessages.tsx`
- `frontend/app/shared/_components/SharedChatTokenStats.tsx`
- `frontend/app/shared/_components/SharedChatFooter.tsx`

### Modified Files

**Backend:**
- `backend/api/v0/__init__.py` (register new router)
- `backend/api/deps.py` (add new dependency injections)
- `backend/models/__init__.py` (export new model)

**Frontend:**
- `frontend/stores/chatStore/actions.ts` (add share action)
- `frontend/stores/chatStore/types.ts` (add share types if needed)
- `frontend/app/prompts/_components/ChatSimpleHeader.tsx` (add share button)
- `frontend/next.config.js` (proxy configuration)

---

## Acceptance Criteria

- [ ] User can click "Share" button in chat header
- [ ] Share button generates a unique URL
- [ ] URL can be copied to clipboard
- [ ] Shared URL is publicly accessible (no auth required)
- [ ] Shared view displays all messages in read-only mode
- [ ] Shared view shows model name and provider
- [ ] Shared view shows token usage (input, output, reasoning per message)
- [ ] Shared view shows total cost
- [ ] Shared view shows inference time per message
- [ ] No input field, reset button, or edit capabilities in shared view
- [ ] Shared view handles tool calls display
- [ ] Invalid share IDs show appropriate error page
- [ ] Unit tests pass for backend service
- [ ] API endpoints follow standard response pattern
