'use client';

import { useEffect } from 'react';
import { useIsAuthenticated, useAuthActions } from '@/stores/authStore';
import { useHostingType } from '@/stores/sidebarStore';
import { ConfigService } from '@/services/config/configService';
import { UserProfile } from './UserProfile';
import { LoginButton } from './LoginButton';
import { LogoutButton } from './LogoutButton';

interface AuthSectionProps {
  isCollapsed?: boolean;
  textColor?: string;
  mutedTextColor?: string;
  hoverBg?: string;
  activeBg?: string;
  userProfileBg?: string;
  borderColor?: string;
}

export const AuthSection = (props: AuthSectionProps) => {
  const isAuthenticated = useIsAuthenticated();
  const { initializeAuth } = useAuthActions();
  const hostingType = useHostingType();

  // Initialize auth state when component mounts
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <>
      {/* User Profile Section - Only show when authenticated */}
      {isAuthenticated && (
        <UserProfile {...props} />
      )}

      {/* GitHub Login or Logout Button - Hidden for individual hosting */}
      {!ConfigService.shouldSkipAuth(hostingType) && isAuthenticated ? (
        <LogoutButton {...props} />
      ) : !ConfigService.shouldSkipAuth(hostingType) ? (
        <LoginButton {...props} />
      ) : null}
    </>
  );
};