'use client';

import { Center, Text, VStack } from '@chakra-ui/react';
import { useAuthActions, useGithubCallbackStatus } from '@/stores/authStore';
import { useLayoutEffect } from 'react';

export default function GitHubCallbackPage() {
  const { handleGithubCallback } = useAuthActions();
  const { error } = useGithubCallbackStatus();

  // Use useLayoutEffect to trigger the callback before browser paints
  // This ensures it runs immediately on mount
  useLayoutEffect(() => {
    handleGithubCallback();
  }, []); // Empty deps array ensures this only runs once

  // Minimal UI - the global loading overlay handles the loading state
  // Only show error if authentication actually fails
  return (
    <Center height="100vh" width="100%">
      <VStack gap={6}>
        {error && (
          <>
            <Text fontSize="lg" fontWeight="medium" color="red.500">
              Authentication Failed
            </Text>
            <Text fontSize="sm" color="gray.500">
              {error}. Redirecting you...
            </Text>
          </>
        )}
      </VStack>
    </Center>
  );
}