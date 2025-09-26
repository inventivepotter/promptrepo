'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';
import { Center, Text, VStack } from '@chakra-ui/react';
import { useAuthActions, useAuthStore } from '@/stores/authStore';
import { errorNotification } from '@/lib/notifications';

export default function GitHubCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { oauthCallbackGithub } = useAuthActions();
  
  // Subscribe to store state for error feedback
  const error = useAuthStore((state) => state.error);

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');

      if (code && state) {
        try {
          // Await the async action to ensure it completes before proceeding.
          await oauthCallbackGithub(code, state);
          
          // After the action completes, the store will have the redirect URL.
          const promptRepoRedirectUrl = useAuthStore.getState().promptrepoRedirectUrl;
          router.push(promptRepoRedirectUrl);
        } catch (err) {
          // This catch block will handle errors thrown by oauthCallbackGithub.
          // The store might also update its error state, but this provides a direct path.
          console.error('Callback processing error:', err);
          errorNotification('Authentication Error', 'An error occurred during authentication.');
          router.push('/');
        }
      } else {
        // If code or state is missing, it's an error.
        errorNotification('Authentication Error', 'Authorization code or state not found.');
        router.push('/');
      }
    };

    processCallback();
  }, [searchParams, oauthCallbackGithub, router]);

  // Render UI based on the Zustand store's state
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