'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box, Center, Spinner, Text, VStack } from '@chakra-ui/react';
import { handleAuthCallback } from '../../../_lib/handleAuthCallback';
import { errorNotification } from '@/lib/notifications';

export default function GitHubCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const processCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');

        if (!code || !state) {
          errorNotification(
            'Authentication Error',
            'Missing authorization code or state parameter'
          );
          router.push('/');
          return;
        }

        // Handle the authentication callback
        const result = await handleAuthCallback(code, state);

        if (result) {
          // Success - redirect to the main application
          router.push('/');
        } else {
          // Failed - redirect to home or login page
          router.push('/');
        }
      } catch (error) {
        console.error('Callback processing error:', error);
        errorNotification(
          'Authentication Error',
          'An error occurred during authentication'
        );
        router.push('/');
      }
    };

    processCallback();
  }, [searchParams, router]);

  return (
    <Center height="100vh" width="100%">
      <VStack gap={6}>
        <Spinner size="xl" color="blue.500" />
        <Text fontSize="lg" fontWeight="medium">
          Logging you in...
        </Text>
        <Text fontSize="sm" color="gray.500">
          Please wait while we complete your GitHub authentication
        </Text>
      </VStack>
    </Center>
  );
}