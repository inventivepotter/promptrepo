# Store Architecture Pattern

## Introduction

This document describes the standardized store architecture pattern established through the refactoring of all frontend stores in the application. This pattern provides a consistent, maintainable approach to managing client-side state with localStorage and sessionStorage.

### Purpose

The standardized store architecture pattern aims to:
- Provide a consistent API across all stores
- Ensure SSR safety with browser environment checks
- Implement robust error handling
- Centralize storage key management
- Maintain backward compatibility
- Improve code maintainability and developer experience

### Benefits

- **Consistency**: All stores follow the same patterns and conventions
- **Type Safety**: Full TypeScript support with proper type definitions
- **SSR Safety**: Built-in browser environment checks prevent SSR errors
- **Error Resilience**: Graceful error handling prevents application crashes
- **Maintainability**: Clear structure makes stores easy to understand and modify
- **Backward Compatibility**: Existing code continues to work with export aliases

## Architecture Overview

The store architecture follows a functional programming approach with pure functions that interact with browser storage APIs. Each store module exports a collection of functions organized by responsibility:

```
Store Module
├── Core Storage Functions (CRUD operations)
├── Domain-Specific Operations
├── Query Functions
├── Utility Functions
└── Backward Compatibility Exports
```

### Key Principles

1. **Functional Approach**: No classes or complex state management - just pure functions
2. **Single Responsibility**: Each function has one clear purpose
3. **Defensive Programming**: Always check browser environment and handle errors
4. **Centralized Constants**: All storage keys defined in one place
5. **Type Safety**: Proper TypeScript types for all operations

## Implementation Guidelines

### 1. File Structure

Create store files in the `frontend/stores/` directory with descriptive names:

```
frontend/stores/
├── authStore.ts          # Authentication state
├── pricingStore.ts       # Pricing data cache
├── promptsStore.ts       # User prompts
└── configuredModelsStore.ts  # Model configurations
```

### 2. Import Dependencies

Start with necessary imports:

```typescript
import { localStorage } from "@/lib/localStorage";
import { LOCAL_STORAGE_KEYS } from "@/utils/localStorageConstants";
import type { YourType } from "@/types/...";
```

### 3. Define Type Interfaces

Define clear type interfaces for your data:

```typescript
interface StorageData {
  id: string;
  name: string;
  timestamp: number;
  // ... other fields
}

interface CachedData {
  data: StorageData;
  timestamp: number;
}
```

### 4. Use Centralized Storage Keys

Reference keys from the centralized constants:

```typescript
const STORE_NAME = LOCAL_STORAGE_KEYS;

// Usage
localStorage.set(STORE_NAME.YOUR_KEY, data);
```

### 5. Core Function Structure

Follow this template for storage functions:

```typescript
/**
 * Description of what the function does
 * @param param - Description of parameter
 * @returns Description of return value
 */
export const functionName = (param: Type): ReturnType => {
  // 1. Browser environment check
  if (typeof window === 'undefined') return defaultValue;
  
  try {
    // 2. Core logic
    const result = /* your logic */;
    
    // 3. Validation (if needed)
    if (!isValid(result)) {
      return defaultValue;
    }
    
    // 4. Return result
    return result;
  } catch (error) {
    // 5. Error handling
    console.error('Descriptive error message:', error);
    return defaultValue;
  }
};
```

## Naming Conventions

### Function Names

Use clear, action-oriented names without redundant suffixes:

✅ **Good** (Simplified names):
- `getSession()` - Gets session data
- `setUserData()` - Sets user data
- `clearPrompts()` - Clears prompts
- `hasProvider()` - Checks if provider exists

❌ **Avoid** (Redundant suffixes):
- `getSessionFromStorage()`
- `setUserDataToStorage()`
- `clearPromptsFromStorage()`
- `isProviderInStorage()`

### Function Prefixes

Use consistent prefixes to indicate function behavior:

- **`get`** - Retrieves data: `getPrompts()`, `getSession()`
- **`set`** - Stores data: `setPricingData()`, `setRefreshToken()`
- **`clear`** - Removes data: `clearSession()`, `clearPrompts()`
- **`has`** - Checks existence: `hasPrompt()`, `hasProvider()`
- **`is`** - Boolean state checks: `isUserAuthenticated()`
- **`update`** - Modifies existing data: `updatePrompt()`, `updateSessionExpiry()`
- **`add`** - Adds new items: `addPrompt()`, `addConfiguredModel()`
- **`remove`** - Deletes specific items: `removePrompt()`, `removeConfiguredModel()`
- **`search`** - Queries data: `searchPrompts()`, `searchModels()`

## Code Structure and Organization

### Section Organization

Organize functions into logical sections with clear comments:

```typescript
// ==========================================
// Core Storage Functions
// ==========================================

export const setData = (data: Type): void => { /* ... */ };
export const getData = (): Type | null => { /* ... */ };
export const clearData = (): void => { /* ... */ };

// ==========================================
// CRUD Operations
// ==========================================

export const addItem = (item: Type): void => { /* ... */ };
export const updateItem = (id: string, item: Type): void => { /* ... */ };
export const removeItem = (id: string): void => { /* ... */ };

// ==========================================
// Query Operations
// ==========================================

export const hasItem = (id: string): boolean => { /* ... */ };
export const searchItems = (query: string): Type[] => { /* ... */ };

// ==========================================
// Backward Compatibility Exports
// ==========================================

export const getDataFromStorage = getData;
export const clearDataFromStorage = clearData;
```

## Error Handling Patterns

### Try-Catch Blocks

Wrap all storage operations in try-catch blocks:

```typescript
export const getPrompts = (): Prompt[] => {
  try {
    if (typeof window === 'undefined') return [];
    
    const saved = localStorage.get<PromptJson[]>(STORE_NAME.PROMPTS_DATA);
    if (!saved || !Array.isArray(saved)) {
      return [];
    }
    
    // Validation logic
    const isValid = validateData(saved);
    if (!isValid) {
      console.warn('Invalid data structure found in localStorage');
      return [];
    }
    
    return saved;
  } catch (error) {
    console.error('Failed to get prompts:', error);
    return [];
  }
};
```

### Graceful Degradation

Always provide sensible defaults when errors occur:

```typescript
// Return empty array for list operations
catch (error) {
  console.error('Failed to get items:', error);
  return [];
}

// Return null for single item operations
catch (error) {
  console.error('Failed to get item:', error);
  return null;
}

// Return false for boolean operations
catch (error) {
  console.error('Failed to check status:', error);
  return false;
}
```

## Browser Environment Checks

### SSR Safety

Always check for browser environment before accessing window-dependent APIs:

```typescript
export const storeData = (data: DataType): void => {
  // Early return for SSR
  if (typeof window === 'undefined') return;
  
  // Safe to use browser APIs
  localStorage.set(STORE_NAME.DATA_KEY, data);
};

export const getData = (): DataType | null => {
  // Return default for SSR
  if (typeof window === 'undefined') return null;
  
  // Safe to use browser APIs
  return localStorage.get<DataType>(STORE_NAME.DATA_KEY);
};
```

### Storage API Choice

Choose the appropriate storage API based on data sensitivity:

```typescript
// Use localStorage for persistent data
localStorage.set(STORE_NAME.PERSISTENT_DATA, data);

// Use sessionStorage for sensitive/temporary data
sessionStorage.setItem(STORE_NAME.USER_DATA, JSON.stringify(userData));
```

## Use of Centralized Constants

### Defining Constants

All storage keys are defined in `frontend/utils/localStorageConstants.ts`:

```typescript
export const LOCAL_STORAGE_KEYS = {
  /** Key for storing prompts data */
  PROMPTS_DATA: 'promptsData',
  
  /** Key for storing configured repositories */
  CONFIGURED_REPOS: 'configuredRepos',
  
  /** Key for storing configured models */
  CONFIGURED_MODELS: 'configuredModels',
  
  /** Key for storing pricing data */
  PRICING_DATA: 'pricingData',
  
  /** Key for storing auth session */
  AUTH_SESSION: 'auth_session',
  
  /** Key for storing user data (in sessionStorage) */
  USER_DATA: 'user_data',
  
  /** Key for storing refresh token */
  REFRESH_TOKEN: 'refresh_token'
} as const;
```

### Using Constants in Stores

Reference the centralized keys:

```typescript
import { LOCAL_STORAGE_KEYS } from '@/utils/localStorageConstants';

const STORE_NAME = LOCAL_STORAGE_KEYS;

// Usage
localStorage.set(STORE_NAME.PROMPTS_DATA, prompts);
const data = localStorage.get(STORE_NAME.PROMPTS_DATA);
```

## Backward Compatibility Strategy

### Export Aliases

Maintain backward compatibility by exporting aliases at the end of the file:

```typescript
// ==========================================
// Backward Compatibility Exports
// ==========================================

// Original verbose names → New simplified names
export const getPromptsFromStorage = getPrompts;
export const clearPromptsFromStorage = clearPrompts;
export const addPromptToStorage = addPrompt;
export const updatePromptInStorage = updatePrompt;
export const removePromptFromStorage = removePrompt;
export const isPromptInStorage = hasPrompt;
export const getPromptFromStorage = getPrompt;
export const searchPromptsInStorage = searchPrompts;
```

This allows existing code to continue working while new code uses the simplified names.

## Real Examples from Refactored Stores

### Example 1: Auth Store - Session Management

```typescript
/**
 * Get session data from localStorage
 * @returns Session data if valid and not expired, null otherwise
 */
export const getSession = (): StorageData | null => {
  try {
    if (typeof window === 'undefined') return null;
    
    const session = localStorage.get<StorageData>(STORE_NAME.AUTH_SESSION);
    if (!session) return null;

    // Check if session is expired
    if (new Date() > new Date(session.expiresAt)) {
      clearSession();
      return null;
    }

    return session;
  } catch (error) {
    console.error('Failed to get session:', error);
    return null;
  }
};
```

### Example 2: Pricing Store - Cached Data with Expiry

```typescript
/**
 * Get pricing data from localStorage with cache age checking
 * @param maxAge - Maximum age of cache in milliseconds (default: 24 hours)
 * @returns Pricing data if valid and not expired, null otherwise
 */
export const getPricingData = (maxAge: number = 24 * 60 * 60 * 1000): PricingData | null => {
  const cached = localStorage.get<CachedPricingData>(STORE_NAME.PRICING_DATA);
  if (!cached) return null;
  
  try {
    // Check if cache is expired
    const age = Date.now() - cached.timestamp;
    if (age > maxAge) {
      clearPricingData();
      return null;
    }
    
    // Validate the data structure
    const isValidPricingData = typeof cached.data === 'object' && cached.data !== null;
    if (!isValidPricingData) {
      console.warn('Invalid pricing data structure found in localStorage');
      clearPricingData();
      return null;
    }
    
    return cached.data;
  } catch (error) {
    console.error('Failed to parse cached pricing data:', error);
    clearPricingData();
    return null;
  }
};
```

### Example 3: Prompts Store - CRUD Operations

```typescript
/**
 * Add a new prompt to storage
 * @param newPrompt - New prompt object to add
 */
export const addPrompt = (newPrompt: Prompt): void => {
  try {
    const currentPrompts = getPrompts();
    const promptWithTimestamps = {
      ...newPrompt,
      created_at: newPrompt.created_at || new Date(),
      updated_at: newPrompt.updated_at || new Date()
    };
    const updatedPrompts = [...currentPrompts, promptWithTimestamps];
    storePrompts(updatedPrompts);
  } catch (error) {
    console.error('Failed to add prompt:', error);
    throw new Error('Failed to add prompt');
  }
};
```

### Example 4: Configured Models Store - Provider Operations

```typescript
/**
 * Gets all configured models from localStorage
 * @returns Array of configured provider info or empty array
 */
export const getConfiguredModels = (): ProviderInfo[] => {
  if (typeof window === 'undefined') {
    return [];
  }

  try {
    const saved = localStorage.get<ProviderInfo[]>(LOCAL_STORAGE_KEYS.CONFIGURED_MODELS);
    if (!saved || !Array.isArray(saved)) {
      return [];
    }
    
    // Validate the data structure
    const isValidProviderArray = saved.every((item: unknown) =>
      item && typeof item === 'object' &&
      'id' in item && typeof item.id === 'string' &&
      'name' in item && typeof item.name === 'string' &&
      'models' in item && Array.isArray(item.models)
    );
    
    return isValidProviderArray ? saved as ProviderInfo[] : [];
  } catch (error) {
    console.error('Error getting configured models from storage:', error);
    return [];
  }
};
```

## Best Practices

### Do's ✅

1. **Always include browser environment checks** for SSR safety
2. **Use try-catch blocks** for all storage operations
3. **Provide meaningful error messages** in console.error statements
4. **Return sensible defaults** when errors occur
5. **Validate data structure** before returning from storage
6. **Use TypeScript types** for all parameters and return values
7. **Write clear JSDoc comments** for all exported functions
8. **Group related functions** with section comments
9. **Use centralized storage keys** from localStorageConstants
10. **Maintain backward compatibility** with export aliases

### Don'ts ❌

1. **Don't throw errors** in getter functions - return defaults instead
2. **Don't use verbose function names** with "FromStorage" suffixes
3. **Don't access window directly** without environment checks
4. **Don't parse JSON manually** - use the localStorage wrapper
5. **Don't mutate data directly** - create new objects/arrays
6. **Don't skip validation** when retrieving complex data structures
7. **Don't mix storage APIs** - be consistent within a store
8. **Don't hardcode storage keys** - use centralized constants
9. **Don't forget error handling** - always use try-catch
10. **Don't break existing APIs** - use aliases for compatibility

## Migration Guide for Creating New Stores

### Step 1: Create the Store File

Create a new file in `frontend/stores/`:

```typescript
// frontend/stores/myNewStore.ts
import { localStorage } from "@/lib/localStorage";
import { LOCAL_STORAGE_KEYS } from "@/utils/localStorageConstants";
```

### Step 2: Add Storage Key

Update `frontend/utils/localStorageConstants.ts`:

```typescript
export const LOCAL_STORAGE_KEYS = {
  // ... existing keys
  
  /** Key for storing my new data */
  MY_NEW_DATA: 'myNewData'
} as const;
```

### Step 3: Define Types

```typescript
interface MyData {
  id: string;
  value: string;
  timestamp: Date;
}

interface CachedMyData {
  data: MyData[];
  timestamp: number;
}
```

### Step 4: Implement Core Functions

```typescript
const STORE_NAME = LOCAL_STORAGE_KEYS;

/**
 * Store my data to localStorage
 * @param data - Data to store
 */
export const setMyData = (data: MyData[]): void => {
  try {
    if (typeof window === 'undefined') return;
    
    const cached: CachedMyData = {
      data,
      timestamp: Date.now()
    };
    
    localStorage.set(STORE_NAME.MY_NEW_DATA, cached);
  } catch (error) {
    console.error('Failed to store my data:', error);
    throw new Error('Failed to store data');
  }
};

/**
 * Get my data from localStorage
 * @returns Data array or empty array
 */
export const getMyData = (): MyData[] => {
  try {
    if (typeof window === 'undefined') return [];
    
    const cached = localStorage.get<CachedMyData>(STORE_NAME.MY_NEW_DATA);
    if (!cached?.data) return [];
    
    return cached.data;
  } catch (error) {
    console.error('Failed to get my data:', error);
    return [];
  }
};

/**
 * Clear my data from localStorage
 */
export const clearMyData = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.clear(STORE_NAME.MY_NEW_DATA);
};
```

### Step 5: Add Domain-Specific Functions

```typescript
/**
 * Add a new item to my data
 * @param item - Item to add
 */
export const addItem = (item: MyData): void => {
  const current = getMyData();
  const updated = [...current, item];
  setMyData(updated);
};

/**
 * Check if item exists
 * @param id - Item ID to check
 * @returns True if exists, false otherwise
 */
export const hasItem = (id: string): boolean => {
  const items = getMyData();
  return items.some(item => item.id === id);
};
```

### Step 6: Add Backward Compatibility (if migrating)

```typescript
// If migrating from old naming convention
export const getMyDataFromStorage = getMyData;
export const clearMyDataFromStorage = clearMyData;
export const addItemToStorage = addItem;
export const hasItemInStorage = hasItem;
```

## Testing Considerations

When testing stores, consider:

1. **Mock browser environment** for SSR tests
2. **Test error scenarios** with invalid data
3. **Verify data validation** logic
4. **Test cache expiry** for time-based caches
5. **Ensure backward compatibility** exports work

Example test structure:

```typescript
describe('myStore', () => {
  beforeEach(() => {
    // Clear storage before each test
    localStorage.clear();
  });
  
  it('should handle SSR environment', () => {
    // Mock SSR environment
    const originalWindow = global.window;
    delete global.window;
    
    expect(getMyData()).toEqual([]);
    
    global.window = originalWindow;
  });
  
  it('should store and retrieve data', () => {
    const testData = [{ id: '1', value: 'test', timestamp: new Date() }];
    setMyData(testData);
    
    const retrieved = getMyData();
    expect(retrieved).toEqual(testData);
  });
});
```

## Conclusion

The standardized store architecture pattern provides a robust, maintainable approach to client-side state management. By following these patterns and conventions, developers can:

- Create consistent, predictable stores
- Avoid common pitfalls with SSR and error handling
- Maintain backward compatibility
- Write cleaner, more maintainable code

When creating new stores or refactoring existing ones, refer to this guide and the existing store implementations as templates. The patterns established here have been proven through successful refactoring of all application stores and provide a solid foundation for future development.