# Type Sharing Between Backend and Frontend

This document explains how to share request/response structures between the Python/FastAPI backend and TypeScript frontend.

## Overview

Since our backend uses FastAPI with Pydantic models and the frontend uses TypeScript, we need a way to keep the types synchronized. FastAPI automatically generates OpenAPI schemas from Pydantic models, which we can use to generate TypeScript types.

## Approaches

### 1. **Automatic Type Generation from OpenAPI Schema** (Recommended)

FastAPI automatically generates an OpenAPI schema that includes all your Pydantic models. We can use this to generate TypeScript types.

#### Setup

1. Install the required npm package:
```bash
cd frontend
npm install -D openapi-typescript
```

2. Run the type sync script:
```bash
python scripts/sync-types.py
```

This will:
- Extract the OpenAPI schema from your FastAPI app
- Generate TypeScript interfaces for all Pydantic models
- Save them to `frontend/types/generated/backend-types.ts`

#### Benefits
- Single source of truth (Pydantic models)
- Automatic synchronization
- Includes validation rules and descriptions
- No manual maintenance

### 2. **Shared Schema Files** (Alternative)

For complex projects, you might want to define schemas in a shared format:

```
shared/
├── schemas/
│   ├── user.yaml       # YAML schema definitions
│   ├── config.yaml
│   └── ...
```

Then generate both Python and TypeScript from these schemas.

### 3. **Runtime Validation** (Additional Safety)

Use runtime validation libraries to ensure type safety:

**Frontend (TypeScript):**
```typescript
import { z } from 'zod';

// Define schema
const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

// Runtime validation
const validateUser = (data: unknown): User => {
  return UserSchema.parse(data);
};
```

**Backend (Python):**
```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
```

## Implementation Steps

### Step 1: Define Pydantic Models in Backend

Create your Pydantic models in the backend:

```python
# backend/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
```

### Step 2: Use Models in FastAPI Endpoints

```python
# backend/api/v0/users.py
from fastapi import APIRouter
from schemas.user import UserCreate, UserResponse
from middlewares.rest import StandardResponse, success_response

router = APIRouter()

@router.post("/", response_model=StandardResponse[UserResponse])
async def create_user(user: UserCreate) -> StandardResponse[UserResponse]:
    # Create user logic
    created_user = ...
    return success_response(data=created_user)
```

### Step 3: Generate TypeScript Types

Run the sync script to generate TypeScript types:

```bash
# From project root
python scripts/sync-types.py

# Or add to package.json
npm run sync-types
```

### Step 4: Use Generated Types in Frontend

```typescript
// frontend/app/users/api.ts
import { UserResponse, UserCreate } from '@/types/generated/backend-types';
import { StandardResponse } from '@/types/OpenApiResponse';
import httpClient from '@/lib/httpClient';

export class UsersApi {
  static async createUser(user: UserCreate): Promise<StandardResponse<UserResponse>> {
    return httpClient.post<UserResponse>('/api/v0/users', user);
  }
}
```

## Package.json Scripts

Add these scripts to your frontend's package.json:

```json
{
  "scripts": {
    "sync-types": "python ../scripts/sync-types.py",
    "generate-types": "bash ../scripts/generate-types.sh",
    "type-check": "tsc --noEmit"
  }
}
```

## Best Practices

1. **Always define models in backend first** - Pydantic models are the source of truth
2. **Run type sync in CI/CD** - Ensure types are always in sync
3. **Use strict TypeScript** - Enable strict mode in tsconfig.json
4. **Version your API** - Use versioned endpoints (e.g., `/api/v1/`)
5. **Document breaking changes** - When changing models, document migration steps

## Common Patterns

### Paginated Responses

**Backend (Python):**
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
```

**Frontend (TypeScript):**
```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}
```

### Enum Sharing

**Backend (Python):**
```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
```

**Frontend (TypeScript):**
```typescript
export enum UserRole {
  ADMIN = "admin",
  USER = "user",
  GUEST = "guest"
}
```

## Troubleshooting

### Types out of sync
- Run `npm run sync-types` to regenerate
- Check that all Pydantic models are properly imported in your FastAPI app
- Ensure the backend server can start without errors

### Missing types
- Make sure the endpoint is registered in FastAPI
- Check that response_model is specified in the route decorator
- Verify the Pydantic model is properly defined

### Type conflicts
- Use unique names for your models
- Avoid using reserved TypeScript keywords
- Consider namespacing (e.g., `UserModels.CreateRequest`)

## Advanced: Custom Type Mappings

For special Python types that don't map directly to TypeScript:

```python
# backend/schemas/custom_types.py
from decimal import Decimal
from pydantic import BaseModel, Field

class PriceResponse(BaseModel):
    amount: Decimal = Field(..., description="Price in decimal format")
    currency: str = Field(..., description="ISO 4217 currency code")
    
    class Config:
        json_encoders = {
            Decimal: str  # Serialize Decimal as string
        }
```

Then in TypeScript:
```typescript
interface PriceResponse {
  amount: string;  // Decimal represented as string
  currency: string;
}
```

## Workflow Summary

1. **Backend Developer**: Creates/updates Pydantic models
2. **Run sync**: `npm run sync-types` 
3. **Frontend Developer**: Uses generated types
4. **CI/CD**: Validates types match on every commit

This ensures type safety across your full stack application!