import { usePathname } from 'next/navigation';
import { authService } from '@/services/auth/authService';

/**
 * Hook for handling login with automatic redirect to current page.
 * Uses the current pathname as the PromptRepo redirect URL.
 */
export function useLogin() {
  const pathname = usePathname();

  /**
   * Initiate login flow with optional custom redirect URL
   * @param customRedirectUrl - Optional custom redirect URL, defaults to current pathname
   */
  const login = async (customRedirectUrl?: string) => {
    try {
      // Use custom redirect URL or current pathname
      const promptrepoRedirectUrl = customRedirectUrl || pathname;
      
      // Get the OAuth authorization URL from the backend
      const authUrl = await authService.getAuthUrl(promptrepoRedirectUrl);
      
      if (authUrl) {
        // Redirect to the OAuth provider's authorization URL
        window.location.href = authUrl;
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  return { login };
}