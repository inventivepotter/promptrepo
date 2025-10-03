# Page Authentication Protection

This guide explains how to protect pages in your Next.js application so they only load if the user is authenticated, otherwise redirecting to the homepage.

## ProtectedRoute Component

The `ProtectedRoute` component is a wrapper that checks authentication status before rendering its children. It handles:

- Checking if the user is authenticated
- Showing a loading state while checking authentication
- Displaying an unauthorized screen or redirecting if not authenticated
- Rendering the protected content if authenticated

### Usage

Basic usage:

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function ProtectedPage() {
  return (
    <ProtectedRoute>
      {/* Your protected content here */}
      <div>This content is only visible to authenticated users</div>
    </ProtectedRoute>
  );
}
```

### Props

The `ProtectedRoute` component accepts the following props:

- `children` (React.ReactNode): The content to render if authenticated
- `redirectTo` (string, optional): The URL to redirect to if not authenticated (defaults to '/')
- `showUnauthorizedScreen` (boolean, optional): Whether to show an unauthorized screen before redirecting (defaults to true)

### Examples

#### Basic Protection

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <div>Settings page content</div>
    </ProtectedRoute>
  );
}
```

#### Custom Redirect URL

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function DashboardPage() {
  return (
    <ProtectedRoute redirectTo="/login">
      <div>Dashboard content</div>
    </ProtectedRoute>
  );
}
```

#### Hide Unauthorized Screen (Immediate Redirect with Toast)

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function AdminPage() {
  return (
    <ProtectedRoute
      redirectTo="/login"
      showUnauthorizedScreen={false}
    >
      <div>Admin content</div>
    </ProtectedRoute>
  );
}
```

When `showUnauthorizedScreen` is set to `false`, the component will immediately redirect the user to the specified URL and show a toast notification informing them that authentication is required.

#### Show Unauthorized Screen (No Redirect)

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function SecurePage() {
  return (
    <ProtectedRoute
      showUnauthorizedScreen={true}
    >
      <div>Secure content</div>
    </ProtectedRoute>
  );
}
```

When `showUnauthorizedScreen` is set to `true` (the default), the component will display the UnauthorizedScreen component with a login button, allowing users to authenticate without leaving the page.

## How It Works

1. **Initial Load**: Shows a loading spinner while checking authentication status
2. **Authenticated**: Renders the protected content
3. **Not Authenticated**: 
   - If `showUnauthorizedScreen` is true: Shows an unauthorized screen with a login button
   - Then redirects to the specified URL (or homepage by default)

## Implementation Details

The `ProtectedRoute` component uses the existing auth store hooks:

- `useAuthState`: Gets authentication status, loading state, and initialization status
- `useRouter`: Handles navigation for redirects

The component properly handles:
- Loading states while authentication is being checked
- Authentication initialization
- Session expiration and logout scenarios

## Best Practices

1. **Wrap Entire Pages**: For best results, wrap the entire page content with `ProtectedRoute`
2. **Consistent Redirects**: Use consistent redirect URLs across your application
3. **Loading States**: The component handles loading states automatically, no need for additional loading UI
4. **Error Handling**: Authentication errors are handled by the auth store and displayed appropriately

## Example: Protected Config Page

Here's an example of a protected configuration page:

```tsx
'use client'

import { Box, Container, VStack } from '@chakra-ui/react'
import { ConfigSection, LLMConfigManager, RepoConfigManager } from '@/components/config'
import { ConfigHeader } from '@/components/config/ConfigHeader'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

export default function ConfigPage() {
  return (
    <ProtectedRoute>
      <Box width="100%">
        <VStack gap={8} align="stretch">
          <ConfigHeader />
          <Container maxW="7xl" py={6}>
            <ConfigSection>
              <LLMConfigManager />
              <RepoConfigManager />
            </ConfigSection>
          </Container>
        </VStack>
      </Box>
    </ProtectedRoute>
  )
}
```

This ensures that only authenticated users can access the configuration page, and unauthenticated users will be redirected to the homepage with an option to log in.