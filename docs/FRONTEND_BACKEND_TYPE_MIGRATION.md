# Frontend to Backend Type Migration Strategy

This document outlines the strategy and patterns used to migrate frontend code from using custom frontend types to directly using backend-generated types. This approach eliminates type mapping, ensures type safety, and maintains consistency between frontend and backend.

## Overview

The migration strategy involves replacing custom frontend types with backend-generated OpenAPI types, updating state management, API calls, and error handling to work directly with backend data structures.

## Core Principles

1. **Use Backend Types Directly**: Replace all custom frontend types with types from `@/types/generated/api`
2. **Eliminate Type Mapping**: Remove intermediate transformation layers between backend responses and frontend state
3. **Consistent Error Handling**: Use standardized type guards and error notifications
4. **Simplify State Management**: Update state structures to match backend data schemas

## Step-by-Step Migration Process

### 1. Identify Frontend-Specific Types

Look for custom types that duplicate or transform backend types:
- Configuration interfaces
- Response wrapper types
- Custom state interfaces
- API response models

**Example Before:**
```typescript
export interface Configuration {
  hostingType: "individual" | "organization" | "multi-tenant" | "";
  githubClientId: string;
  githubClientSecret: string;
  llmConfigs: Array<LLMConfig>;
}
```

### 2. Replace with Backend Types

Import and use types from the generated API schema:

**Example After:**
```typescript
import type { components } from '@/types/generated/api';
type AppConfigOutput = components['schemas']['AppConfig-Output'];
```

### 3. Update State Interfaces

Replace frontend types in state interfaces with backend types:

**Before:**
```typescript
export interface ConfigState {
  config: Configuration;
  providers: {
    available: LLMProvider[];
    // ...
  };
}
```

**After:**
```typescript
import type { components } from '@/types/generated/api';

type AppConfigOutput = components['schemas']['AppConfig-Output'];
type BasicProviderInfo = components['schemas']['BasicProviderInfo'];

export interface ConfigState {
  config: AppConfigOutput;
  providers: {
    available: BasicProviderInfo[];
    configured: BasicProviderInfo[];
    // ...
  };
}
```

### 4. Update API Response Handling

Replace custom response handling with proper type guards:

**Before:**
```typescript
const result = await api.getData();
if (!result.success) {
  // Handle error with custom properties
}
return result.data;
```

**After:**
```typescript
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';

const result = await api.getData();

if (isErrorResponse(result)) {
  errorNotification(
    result.title || 'Error',
    result.detail || 'Operation failed'
  );
  throw new Error(result.detail || 'Operation failed');
}

if (isStandardResponse(result) && result.data) {
  return result.data;
}

throw new Error('Unexpected response format');
```

### 5. Update State Management Logic

Modify state management to work with backend field names and structures:

**Before:**
```typescript
const newConfig = {
  provider: selectedProvider,
  model: selectedModel,
  apiKey: apiKey,
  apiBaseUrl: apiBaseUrl
};
```

**After:**
```typescript
const newConfig: LLMConfig = {
  provider: selectedProvider,
  model: selectedModel,
  api_key: apiKey,
  api_base_url: apiBaseUrl,
  scope: 'user'
};
```

### 6. Simplify Function Return Types

Remove wrapper objects and return backend types directly:

**Before:**
```typescript
export const getConfig = async (): Promise<GetConfigResult> => {
  // ... logic
  return {
    config: mappedConfig,
    error: null
  };
};
```

**After:**
```typescript
export const getConfig = async (): Promise<AppConfigOutput> => {
  // ... logic
  return config; // Direct backend type
};
```

## Common Patterns and Solutions

### Pattern 1: API Call with Type Guards

```typescript
export const fetchData = async (): Promise<BackendType> => {
  try {
    const result = await api.getData();

    if (isErrorResponse(result)) {
      errorNotification(
        result.title || 'Error Title',
        result.detail || 'Error detail'
      );
      throw new Error(result.detail || 'Operation failed');
    }

    if (isStandardResponse(result) && result.data) {
      return result.data;
    }

    throw new Error('Unexpected response format');
  } catch (error) {
    errorNotification('Connection Error', 'Unable to connect to service.');
    throw error;
  }
};
```

### Pattern 2: State Update with Backend Types

```typescript
const updateState = useCallback(async () => {
  try {
    const data = await fetchData();
    setState(prev => ({
      ...prev,
      data, // Direct assignment of backend type
      isLoading: false
    }));
  } catch (error) {
    setState(prev => ({
      ...prev,
      isLoading: false
    }));
  }
}, []);
```

### Pattern 3: Form Handling with Backend Field Names

```typescript
const addItem = useCallback(() => {
  const newItem: BackendItemType = {
    field_name: formData.fieldName, // Map to backend field names
    another_field: formData.anotherField,
    status: 'active'
  };

  setState(prev => ({
    ...prev,
    items: [...(prev.items || []), newItem]
  }));
}, [formData]);
```

## Type Import Strategy

### Standard Imports
```typescript
import type { components } from '@/types/generated/api';

// Extract specific types
type SpecificType = components['schemas']['SpecificType'];
type AnotherType = components['schemas']['AnotherType'];
```

### Type Guards
```typescript
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
```

### Error Handling
```typescript
import { errorNotification } from '@/lib/notifications';
```

## File Structure Considerations

### API Layer
- Keep API functions thin, focused on HTTP calls
- Use backend types for parameters and return values
- Handle errors consistently with type guards

### Service Layer  
- Import from `_lib` functions rather than calling APIs directly
- Let service functions handle error notifications
- Return backend types directly

### State Layer
- Use backend types in state interfaces
- Simplify state structure to match backend schemas
- Remove custom error wrapper objects

## Migration Checklist

- [ ] Identify all custom frontend types that duplicate backend types
- [ ] Replace state interfaces with backend types
- [ ] Update API response handling with proper type guards
- [ ] Modify field names to match backend schema (snake_case vs camelCase)
- [ ] Remove type mapping/transformation functions
- [ ] Update error handling to use backend error structure
- [ ] Clean up unused imports and types
- [ ] Test all API interactions and state updates
- [ ] Verify error scenarios work correctly

## Benefits of This Approach

1. **Type Safety**: Direct use of backend types ensures frontend stays in sync with API changes
2. **Reduced Maintenance**: No need to maintain separate frontend type definitions
3. **Consistency**: Same data structures used throughout the application
4. **Error Reduction**: Eliminates mapping bugs and type mismatches
5. **Automatic Updates**: Frontend types update automatically when backend schema changes

## Common Pitfalls to Avoid

1. **Field Name Mismatches**: Backend typically uses snake_case while frontend uses camelCase
2. **Null Handling**: Backend types may include null/undefined that need proper handling
3. **Error Structure**: Don't assume old error response format, use type guards
4. **Optional Fields**: Backend types may have more optional fields than expected
5. **Array Handling**: Check for null arrays from backend before using array methods

## Testing Strategy

1. **Type Checking**: Ensure TypeScript compilation passes without type errors
2. **API Integration**: Test all API calls with both success and error scenarios
3. **State Updates**: Verify state updates correctly with backend data structures
4. **Error Handling**: Test error notifications appear correctly
5. **Data Flow**: Trace data from API response through state to UI components

This migration strategy ensures a smooth transition from frontend-specific types to backend types while maintaining type safety and improving code consistency across the application.