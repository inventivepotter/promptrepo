# OAuth Authentication Flow with PromptRepo Redirect URL

This document explains how the OAuth authentication flow works with support for redirecting users back to their original page after successful authentication.

## Overview

The system maintains two separate redirect URLs:
1. **OAuth Redirect URI**: The callback URL registered with the OAuth provider (e.g., GitHub)
2. **PromptRepo Redirect URL**: The application page where the user initiated login

## Complete OAuth Flow

### Step 1: User Initiates Login
User clicks login from any page in the application (e.g., `/config/repos`).

**Frontend - Auth State Login Function:**
```typescript
// frontend/app/(auth)/_state/authState.ts
const login = useCallback(async (redirectUrl?: string) => {
  try {
    updateAuthState(prev => ({ ...prev, isLoading: true }));

    // Use provided redirect URL or current pathname
    const promptrepoRedirectUrl = redirectUrl || window.location.pathname;
    const authUrl = await authService.getAuthUrl(promptrepoRedirectUrl);

    if (authUrl) {
      window.location.href = authUrl;
    } else {
      errorNotification('Login Failed', 'Unable to initiate login. Please try again.');
    }
  } catch (error) {
    console.error('Login failed:', error);
    updateAuthState(prev => ({ ...prev, isLoading: false }));
    errorNotification('Login Failed', 'Unable to initiate login. Please try again.');
  }
}, [updateAuthState]);
```

**Usage in Components:**
```typescript
// Using the auth hook from AuthProvider
import { useAuth } from '@/app/(auth)/_components/AuthProvider';

function LoginButton() {
  const { login } = useAuth();
  
  return (
    <button onClick={() => login()}>
      Login with GitHub
    </button>
  );
}

// Or using the custom useLogin hook for explicit pathname capture
import { useLogin } from '@/hooks/useLogin';

function AlternativeLoginButton() {
  const { login } = useLogin();
  
  return (
    <button onClick={() => login()}>
      Login with GitHub
    </button>
  );
}
```

### Step 2: Frontend Sends Request to Backend
The frontend captures the current URL and sends it to the backend.

**Frontend API Call:**
```typescript
// frontend/services/auth/api.ts
export const authApi = {
  initiateLogin: async (promptrepoRedirectUrl?: string): Promise<OpenApiResponse<AuthUrlResponseData>> => {
    const params = new URLSearchParams();
    if (promptrepoRedirectUrl) {
      params.append('promptrepo_redirect_url', promptrepoRedirectUrl);
    }
    const queryString = params.toString();
    return await httpClient.get<AuthUrlResponseData>(
      `/api/v0/auth/login/github/${queryString ? `?${queryString}` : ''}`
    );
  },
};
```

### Step 3: Backend Generates OAuth State
Backend generates a unique state and stores metadata including the PromptRepo redirect URL.

**Backend Login Endpoint:**
```python
# backend/api/v0/auth/login/github.py
@router.get("/github/")
async def initiate_github_login(
    promptrepo_redirect_url: Optional[str] = Query(None, description="PromptRepo redirect URL"),
    auth_service: AuthServiceDep = AuthServiceDep
) -> StandardResponse[AuthUrlResponseData]:
    """Initiate GitHub OAuth login."""
    
    # Create login request with optional redirect URL
    login_request = LoginRequest(
        provider=OAuthProvider.GITHUB,
        promptrepo_redirect_url=promptrepo_redirect_url
    )
    
    # Get authorization URL
    auth_url = await auth_service.initiate_oauth_login(login_request)
    
    return success_response(
        data=AuthUrlResponseData(authUrl=auth_url),
        message="GitHub authorization URL generated successfully"
    )
```

### Step 4: Backend Stores State with Metadata
The OAuth service stores the PromptRepo redirect URL in state metadata.

**OAuth Service - Generating Authorization URL:**
```python
# backend/services/oauth/oauth_service.py
async def get_authorization_url(
    self,
    provider: OAuthProvider,
    scopes: Optional[List[str]] = None,
    state: Optional[str] = None,
    promptrepo_redirect_url: Optional[str] = None
) -> AuthUrlResponse:
    """Generate OAuth authorization URL for specified provider."""
    
    # Get OAuth redirect URI from configuration
    oauth_redirect_uri = self.get_provider_config(provider).redirect_url
    
    # Generate unique state
    state = self.state_manager.generate_state()
    
    # Generate authorization URL
    auth_url, provider_state = await oauth_provider.generate_auth_url(
        scopes=scopes or [],
        redirect_uri=oauth_redirect_uri,
        state=state
    )
    
    # Store state with provider info and promptrepo redirect URL
    self.state_manager.store_state(
        state=state,
        provider=provider,
        redirect_uri=oauth_redirect_uri,
        scopes=scopes or [],
        promptrepo_redirect_url=promptrepo_redirect_url  # Stored in metadata
    )
    
    return AuthUrlResponse(
        auth_url=auth_url,
        provider=provider,
        state=state
    )
```

### Step 5-7: OAuth Provider Interaction
- User is redirected to OAuth provider (e.g., GitHub)
- User authorizes the application
- OAuth provider redirects back to the configured redirect_uri

### Step 8-9: Frontend Callback Handling
The frontend callback page receives the authorization code and state from the OAuth provider.

**Frontend Callback Page:**
```typescript
// frontend/app/(auth)/auth/callback/github/page.tsx
export default function GitHubCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');

      if (!code || !state) {
        errorNotification('Authentication Error', 'Missing parameters');
        router.push('/');
        return;
      }

      // Handle the authentication callback (no redirect_uri needed)
      const result = await authService.handleCallback(code, state);

      if (result) {
        // Redirect to the PromptRepo redirect URL if provided
        const redirectUrl = result.promptrepoRedirectUrl || '/';
        router.push(redirectUrl);
      } else {
        router.push('/');
      }
    };

    processCallback();
  }, [searchParams, router]);

  return (
    <Center height="100vh">
      <Spinner size="xl" />
      <Text>Logging you in...</Text>
    </Center>
  );
}
```

### Step 10-13: Backend Validation and Token Exchange
Backend validates the state and exchanges the authorization code for an access token.

**Backend OAuth Service - Token Exchange:**
```python
# backend/services/oauth/oauth_service.py
async def exchange_code_for_token(
    self,
    provider: OAuthProvider,
    code: str,
    state: str,
    redirect_uri: Optional[str] = None  # Optional, fetched from state
) -> OAuthToken:
    """Exchange authorization code for access token."""
    
    # Validate state
    if not self.state_manager.validate_state(state, provider):
        raise InvalidStateError(state, provider)
    
    # Get state data
    state_data = self.state_manager.get_state_data(state)
    if not state_data:
        raise InvalidStateError(state, provider)
    
    # Get redirect URI from state
    stored_redirect_uri = state_data.redirect_uri
    if not stored_redirect_uri:
        raise InvalidStateError("Missing redirect URI in state", provider)
    
    # If redirect_uri is provided, verify it matches for security
    if redirect_uri and redirect_uri != stored_redirect_uri:
        raise InvalidStateError("Redirect URI mismatch", provider)
    
    # Exchange code for token using stored redirect URI
    token = await oauth_provider.exchange_code_for_token(
        code=code,
        redirect_uri=stored_redirect_uri,
        state=state
    )
    
    # Clean up state
    self.state_manager.remove_state(state)
    
    return token
```

### Step 14-15: Backend Returns Response with Redirect URL
Backend retrieves the PromptRepo redirect URL from state metadata and returns it with the session.

**Backend Auth Service - Handling Callback:**
```python
# backend/services/auth/auth_service.py
async def handle_oauth_callback(
    self,
    provider: OAuthProvider,
    code: str,
    state: str,
) -> LoginResponse:
    """Handle OAuth callback and create user session."""
    
    # Get state metadata to retrieve promptrepo_redirect_url
    state_metadata = self.oauth_service.state_manager.get_state_metadata(state)
    promptrepo_redirect_url = state_metadata.get("promptrepo_redirect_url") if state_metadata else None
    
    # Exchange code for token (redirect_uri is fetched from state)
    token_response = await self.oauth_service.exchange_code_for_token(
        provider=provider,
        code=code,
        state=state
    )
    
    # Get user information
    user_info = await self.oauth_service.get_user_info(
        provider=provider,
        access_token=token_response.access_token
    )
    
    # Create or update user and session
    user = await self._create_or_update_user(user_info, provider)
    session = await self.session_service.create_session(user.id)
    
    # Return response with promptrepo redirect URL
    return LoginResponse(
        user=user,
        session_token=session.token,
        expires_at=session.expires_at.isoformat(),
        promptrepo_redirect_url=promptrepo_redirect_url
    )
```

**Backend Callback Endpoint:**
```python
# backend/api/v0/auth/callback/github.py
@router.get("/github/")
async def github_oauth_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF verification"),
    auth_service: AuthServiceDep = AuthServiceDep,
) -> StandardResponse[LoginResponseData]:
    """Handle GitHub OAuth callback."""
    
    # Handle OAuth callback (redirect_uri is retrieved from state)
    login_response = await auth_service.handle_oauth_callback(
        provider=OAuthProvider.GITHUB,
        code=code,
        state=state
    )
    
    # Convert response to expected format
    response_data = LoginResponseData(
        user=login_response.user,
        sessionToken=login_response.session_token,
        expiresAt=login_response.expires_at,
        promptrepoRedirectUrl=login_response.promptrepo_redirect_url
    )
    
    return success_response(
        data=response_data,
        message="User authenticated successfully"
    )
```

### Step 16: Frontend Redirects User
Frontend stores the session and redirects the user back to their original page.

**Frontend Auth Service:**
```typescript
// frontend/services/auth/authService.ts
async handleCallback(code: string, state: string): Promise<LoginResponse | null> {
  try {
    // Exchange code for token (no redirect_uri parameter needed)
    const result = await authApi.exchangeCodeForToken(code, state);
    
    if (!isStandardResponse(result) || !result.data) {
      errorNotification('Authentication Failed', 'Invalid response');
      return null;
    }
    
    // Store session and user data
    this.setSession(result.data.sessionToken, result.data.expiresAt, result.data.user);
    
    // Return the full response including optional promptrepoRedirectUrl
    return result.data;
  } catch (error) {
    errorNotification('Connection Error', 'Authentication failed');
    return null;
  }
}
```

## Security Considerations

### State Validation
The backend performs several security checks:
1. **State exists and is not expired** - Prevents replay attacks
2. **Provider matches** - Ensures the callback is for the correct provider
3. **Redirect URI validation** - If provided, must match stored value
4. **State cleanup** - State is removed after successful use

### Redirect URI Separation
- **OAuth redirect_uri**: Configured in backend environment, never exposed to frontend
- **PromptRepo redirect URL**: User-facing application URL, stored securely in state metadata

## Configuration

### Backend Environment Variables
```env
# OAuth Provider Configuration
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URL=https://yourapp.com/auth/callback/github
```

### Frontend Usage Examples

#### Using the Auth Provider (Recommended)
```typescript
// In any component that needs login
import { useAuth } from '@/app/(auth)/_components/AuthProvider';

function ProtectedPage() {
  const { login, isAuthenticated, user } = useAuth();
  
  // User will be redirected back to current page after login
  const handleLogin = () => {
    login(); // Captures current pathname automatically
  };
  
  // Or specify a custom redirect
  const handleCustomLogin = () => {
    login('/dashboard'); // Redirect to dashboard after login
  };
  
  if (isAuthenticated && user) {
    return <div>Welcome back, {user.name}!</div>;
  }
  
  return (
    <div>
      <button onClick={handleLogin}>
        Login (return to this page)
      </button>
      <button onClick={handleCustomLogin}>
        Login (go to dashboard)
      </button>
    </div>
  );
}
```

#### Using the Custom Hook
```typescript
// Alternative approach using the useLogin hook
import { useLogin } from '@/hooks/useLogin';

function AlternativePage() {
  const { login } = useLogin();
  
  return (
    <button onClick={() => login()}>
      Login with GitHub
    </button>
  );
}
```

## Testing

### Unit Test Example
```python
# backend/tests/unit/services/auth/test_auth_service.py
async def test_handle_oauth_callback_with_promptrepo_redirect():
    """Test OAuth callback returns promptrepo_redirect_url."""
    
    # Setup mock state with promptrepo_redirect_url
    mock_state_metadata = {"promptrepo_redirect_url": "/config/repos"}
    auth_service.oauth_service.state_manager.get_state_metadata.return_value = mock_state_metadata
    
    # Call callback handler
    response = await auth_service.handle_oauth_callback(
        provider=OAuthProvider.GITHUB,
        code="test_code",
        state="test_state"
    )
    
    # Assert promptrepo_redirect_url is returned
    assert response.promptrepo_redirect_url == "/config/repos"
```

## Important Development Note

### State Persistence

**Current Implementation**: The OAuth state manager uses a singleton pattern with in-memory storage for development:

```python
# backend/services/oauth/state_manager_singleton.py
from services.oauth.state_manager import StateManager

# Create a singleton instance that persists across requests
_state_manager_instance = None

def get_state_manager() -> StateManager:
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = StateManager(state_expiry_minutes=10)
    return _state_manager_instance
```

This implementation means:
- States persist across requests in a single server instance
- States are lost when the server restarts
- States are not shared between multiple server instances
- **This is suitable for development only**

**Production Requirements**: For production deployment, you must:
1. **Option 1: Database Persistence**
   - Create an `OAuthState` database model
   - Store states in the database with TTL
   - Clean up expired states periodically
   
2. **Option 2: Redis Cache**
   - Use Redis for distributed state storage
   - Set expiry times on Redis keys
   - Share states across multiple server instances

This ensures states are:
- Persistent across server restarts
- Shared between multiple server instances
- Properly cleaned up after expiration

## Troubleshooting

### Common Issues

1. **"State not found" errors**
   - **In development**: Server may have restarted, losing in-memory states
   - **Solution**: The singleton pattern helps persist states during development
   - **In production**: Implement database or Redis persistence
   - Check that the state hasn't expired (default TTL: 10 minutes)

2. **Always redirecting to /dashboard instead of original page**
   - **Cause**: The login function was hardcoded to redirect to `/dashboard`
   - **Fix**: Update `authState.ts` to capture current pathname:
     ```typescript
     const promptrepoRedirectUrl = redirectUrl || window.location.pathname;
     ```
   - Ensure components are using the updated `login` function from `useAuth()`

3. **User not redirected to original page**
   - Verify the login function is capturing pathname correctly
   - Check browser console for the actual `promptrepoRedirectUrl` being sent
   - Verify the backend is storing and returning the URL in the response

4. **State validation errors**
   - Ensure state TTL is sufficient (default: 10 minutes)
   - Check that the same state is being used throughout the flow
   - Verify the state manager singleton is initialized properly

5. **Redirect URI mismatch**
   - OAuth redirect URI is configured in backend environment
   - Frontend should NOT send redirect_uri in callback
   - Verify environment variable: `GITHUB_REDIRECT_URL`

## Summary

This implementation provides a secure and user-friendly OAuth flow that:
- **Maintains user context**: Users return to their original page after authentication
- **Separates concerns**: OAuth redirect URI (technical) vs PromptRepo redirect URL (user experience)
- **Provides security**: State validation, CSRF protection, and redirect URI verification
- **Supports flexibility**: Optional custom redirect URLs for specific use cases
- **Development ready**: Singleton state manager for local development
- **Production ready**: Clear upgrade path to database or Redis persistence

## Key Implementation Files

### Backend
- `backend/services/oauth/state_manager.py` - State management logic
- `backend/services/oauth/state_manager_singleton.py` - Singleton wrapper for development
- `backend/services/oauth/oauth_service.py` - OAuth flow orchestration
- `backend/services/auth/auth_service.py` - Authentication business logic
- `backend/api/v0/auth/login/github.py` - Login endpoint
- `backend/api/v0/auth/callback/github.py` - Callback endpoint

### Frontend
- `frontend/app/(auth)/_state/authState.ts` - Core auth state management
- `frontend/app/(auth)/_components/AuthProvider.tsx` - Auth context provider
- `frontend/hooks/useLogin.ts` - Custom login hook
- `frontend/services/auth/authService.ts` - Auth service layer
- `frontend/services/auth/api.ts` - Auth API calls
- `frontend/app/(auth)/auth/callback/github/page.tsx` - OAuth callback handler