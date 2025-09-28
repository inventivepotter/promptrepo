'use client';

import { useEffect } from 'react';
import { useIsAuthenticated, useAuthActions } from '@/stores/authStore';
import { useHostingType, useConfigStore } from '@/stores/configStore';
import { ConfigService } from '@/services/config/configService';
import { UserProfile } from './UserProfile';
import { LoginButton } from './LoginButton';
import { LogoutButton } from './LogoutButton';

interface AuthSectionProps {
  isCollapsed?: boolean;
  hoverBg?: string;
  activeBg?: string;
  userProfileBg?: string;
  borderColor?: string;
}

export const AuthSection = (props: AuthSectionProps) => {
  const isAuthenticated = useIsAuthenticated();
  const { initializeAuth } = useAuthActions();
  const hostingType = useHostingType();
  const config = useConfigStore((state) => state.config);

  // Initialize auth state when component mounts
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Check if GitHub OAuth provider is configured
  const hasGitHubOAuth = config?.oauth_configs?.some(
    (provider) => provider?.provider === 'github'
  );

  // Determine whether to show auth buttons
  const shouldShowAuth = !ConfigService.shouldSkipAuth(hostingType || undefined) && hasGitHubOAuth;

  return (
    <>
      {/* User Profile Section - Only show when authenticated */}
      {isAuthenticated && (
        <UserProfile {...props} />
      )}

      {/* GitHub Login or Logout Button - Only show if GitHub OAuth is configured */}
      {shouldShowAuth && isAuthenticated ? (
        <LogoutButton {...props} />
      ) : shouldShowAuth ? (
        <LoginButton {...props} />
      ) : null}
    </>
  );
};