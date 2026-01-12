'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box, Spinner, Text, VStack } from '@chakra-ui/react';
import { buildEvalEditorUrl } from '@/lib/urlEncoder';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function NewEvalRedirect() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const repoName = searchParams.get('repo_name');

  useEffect(() => {
    if (repoName) {
      // Redirect to the proper eval editor URL with 'new'
      const decodedRepoName = decodeURIComponent(repoName);
      router.replace(buildEvalEditorUrl(decodedRepoName, 'new'));
    } else {
      // No repo specified, redirect to evals list
      router.replace('/evals');
    }
  }, [repoName, router]);

  return (
    <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
      <VStack gap={4}>
        <Spinner size="xl" />
        <Text>Redirecting to eval editor...</Text>
      </VStack>
    </Box>
  );
}

export default function NewEvalPage() {
  return (
    <ProtectedRoute>
      <NewEvalRedirect />
    </ProtectedRoute>
  );
}
