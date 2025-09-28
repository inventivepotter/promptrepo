'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthState } from '@/stores/authStore/hooks';
import { UnauthorizedScreen } from '@/components/UnauthorizedScreen';
import { Box } from '@chakra-ui/react';
import { toaster } from '@/components/ui/toaster';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  showUnauthorizedScreen?: boolean;
}

export function ProtectedRoute({
  children,
  redirectTo = '/',
  showUnauthorizedScreen = true,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, isInitialized } = useAuthState();
  const router = useRouter();

  useEffect(() => {
    // Only redirect if auth is initialized, user is not authenticated, and we're not showing unauthorized screen
    if (isInitialized && !isAuthenticated && !isLoading && !showUnauthorizedScreen) {
      // Show toast notification before redirecting
      toaster.create({
        title: "Authentication Required",
        description: "Please log in to access this page.",
        type: "warning",
        duration: 5000,
      });
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, isInitialized, router, redirectTo, showUnauthorizedScreen]);

  // Show loading spinner while checking authentication
  if (!isInitialized || isLoading) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
      >
        <Box className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900" />
      </Box>
    );
  }

  // If not authenticated and initialized, show unauthorized screen or redirect
  if (!isAuthenticated && isInitialized) {
    if (showUnauthorizedScreen) {
      return (
        <UnauthorizedScreen />
      );
    }
    return null; // Will redirect due to the useEffect
  }

  // User is authenticated, render the protected content
  return <>{children}</>;
}