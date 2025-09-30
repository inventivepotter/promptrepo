'use client';

import React, { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box } from '@chakra-ui/react';
import { Prompt } from '@/types/Prompt';
import {
  useCurrentPrompt,
  usePromptActions,
  useIsUpdating,
} from '@/stores/promptStore';
import { useConfigStore } from '@/stores/configStore';
import { PromptEditor } from '../_components/PromptEditor';
import { LoadingOverlay } from '@/components/LoadingOverlay';

function EditorPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptId = searchParams.get('id');
  
  const currentPrompt = useCurrentPrompt();
  const isUpdating = useIsUpdating();
  const {
    fetchPromptById,
    updatePrompt,
    setCurrentPrompt,
    clearCurrentPrompt,
  } = usePromptActions();
  
  // Get config data from configStore
  const config = useConfigStore(state => state.config);
  const configuredRepos = config.repo_configs || [];

  // Fetch and set the current prompt based on the ID from URL
  useEffect(() => {
    if (promptId) {
      fetchPromptById(promptId);
    } else {
      // No ID provided, redirect to prompts list
      router.push('/prompts');
    }
    
    // Clear current prompt when unmounting
    return () => {
      clearCurrentPrompt();
    };
  }, [promptId]);

  const handleSave = async (updates: Partial<Prompt>) => {
    if (currentPrompt) {
      await updatePrompt(currentPrompt.id, updates);
    }
  };

  const handleBack = () => {
    router.push('/prompts');
  };

  // Transform repos to match the expected Repo type
  const transformedRepos = React.useMemo(() => {
    return configuredRepos.map(config => {
      // Extract owner and repo name from repo_url
      const urlParts = config.repo_url.split('/');
      const repoName = config.repo_name;
      const owner = urlParts[urlParts.length - 2] || 'unknown';
      
      return {
        id: `${owner}/${repoName}`,
        name: repoName,
        full_name: `${owner}/${repoName}`,
        owner: owner,
        provider: 'github', // Default to github
        branch: config.base_branch || config.current_branch || 'main',
        is_public: false
      };
    });
  }, [configuredRepos]);

  return (
    <>
      <LoadingOverlay
        isVisible={isUpdating}
        title="Saving Prompt..."
        subtitle="Please wait while we save your changes"
      />
      <Box minH="100vh">
        <PromptEditor
          prompt={currentPrompt}
          onSave={handleSave}
          onBack={handleBack}
          configuredRepos={transformedRepos}
          isSaving={isUpdating}
        />
      </Box>
    </>
  );
}

export default function EditorPage() {
  return (
    <Suspense fallback={<LoadingOverlay isVisible={true} title="Loading..." subtitle="Loading page data" />}>
      <EditorPageContent />
    </Suspense>
  );
}