'use client';

import { useEffect } from 'react';
import { useIsAuthenticated, useAuthActions } from '@/stores/authStore';
import { useHostingType, useConfigStore } from '@/stores/configStore';
import { ConfigService } from '@/services/config/configService';
import { UserProfile } from './UserProfile';
import { LoginButton } from './LoginButton';
import { LogoutButton } from './LogoutButton';
import type { components } from '@/types/generated/api';

type OAuthProvider = components['schemas']['OAuthProvider'];

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

  // Get all configured OAuth providers
  const configuredProviders = config?.oauth_configs?.map(
    (provider) => provider?.provider as OAuthProvider
  ).filter(Boolean) || [];

  // Determine whether to show auth buttons
  const shouldShowAuth = !ConfigService.shouldSkipAuth(hostingType || undefined) && configuredProviders.length > 0;

  return (
    <>
      {/* User Profile Section - Only show when authenticated */}
      {isAuthenticated && (
        <UserProfile {...props} />
      )}

      {/* Login or Logout Buttons - Only show if OAuth providers are configured */}
      {shouldShowAuth && (
        <>
          {isAuthenticated ? (
            <LogoutButton
              isCollapsed={props.isCollapsed}
              hoverBg={props.hoverBg}
              activeBg={props.activeBg}
            />
          ) : (
            <>
              {configuredProviders.map((provider) => (
                <LoginButton
                  key={provider}
                  provider={provider}
                />
              ))}
            </>
          )}
        </>
      )}
    </>
  );
};