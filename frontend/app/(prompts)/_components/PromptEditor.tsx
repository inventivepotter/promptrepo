'use client';

import { useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  ScrollArea,
} from '@chakra-ui/react';
import { useRouter } from 'next/navigation';
import { PromptEditorHeader } from './PromptEditorHeader';
import { PromptFieldGroup } from './PromptFieldGroup';
import { ModelFieldGroup } from './ModelFieldGroup';
import { ParametersFieldGroup } from './ParametersFieldGroup';
import { Chat } from './Chat';
import { PromptTimeline } from './PromptTimeline';
import { LoadingOverlay } from '@/components/LoadingOverlay';
import { useUser } from '@/stores/authStore';
import { useCurrentPrompt, usePromptActions, useIsUpdating, useIsLoading, useIsChanged } from '@/stores/promptStore/hooks';

export function PromptEditor() {
  const router = useRouter();
  const currentPrompt = useCurrentPrompt();
  const isUpdating = useIsUpdating();
  const isLoading = useIsLoading();
  const isChanged = useIsChanged();
  const { saveCurrentPrompt } = usePromptActions();
  const user = useUser();

  const handleBack = () => {
    router.push('/prompts');
  };

  // Get commits from prompt data with 0th commit for latest changes
  const commits = useMemo(() => {
    const draftCommit = {
      commit_id: '0',
      message: '',
      author: user?.oauth_name || user?.oauth_username || 'Unknown User',
      timestamp: new Date().toISOString(),
      isLatest: true
    };

    if (currentPrompt?.recent_commits && currentPrompt.recent_commits.length > 0) {
      // Add the draft commit at position 0, then the API commits
      return [
        draftCommit,
        ...currentPrompt.recent_commits.map((commit) => ({
          ...commit,
          isLatest: false
        }))
      ];
    }
    
    // Return just the draft commit if no API commits available
    return [draftCommit];
  }, [currentPrompt?.recent_commits, user?.oauth_name, user?.oauth_username]);

  // Show loading overlay while data is being fetched
  if (isLoading || !currentPrompt || !currentPrompt.prompt) {
    return <LoadingOverlay isVisible={true} title="Loading..." subtitle="Loading prompt data" />;
  }

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Sticky Header - Outside ScrollArea */}
      <PromptEditorHeader
        onBack={handleBack}
        onSave={saveCurrentPrompt}
        canSave={!!currentPrompt && isChanged}
        isSaving={isUpdating}
      />

      <ScrollArea.Root flex="1" width="100%">
        <ScrollArea.Viewport
          css={{
            "--scroll-shadow-size": "5rem",
            maskImage:
              "linear-gradient(#000,#000,transparent 0,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            "&[data-at-top]": {
              maskImage:
                "linear-gradient(180deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
            "&[data-at-bottom]": {
              maskImage:
                "linear-gradient(0deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
          }}
        >
          <ScrollArea.Content>
            <Box position="relative">
              {/* Main Content - Three column layout with timeline */}
              <Box p={6}>
                <HStack gap={6} align="start" minH="600px">
                  {/* Left Section - Form */}
                  <Box
                    width="54%"
                  >
                    <VStack gap={6} align="stretch">
                      {/* Basic Info */}
                      <PromptFieldGroup repoName={currentPrompt.repo_name} filePath={currentPrompt.file_path} />
                      
                      {/* Model Configuration */}
                      <ModelFieldGroup />
                      
                      {/* Parameters */}
                      <ParametersFieldGroup />
                    </VStack>
                  </Box>

                  {/* Middle Section - Timeline (1%) */}
                  <Box
                    width="1%"
                    minW="20px"
                    height="200vh"
                    pt={4}
                  >
                    <PromptTimeline commits={commits} />
                  </Box>

                  {/* Right Section - Chat (remaining space) */}
                  <Box
                    width="45%"
                  >
                    <Chat height="700px" />
                  </Box>
                </HStack>
              </Box>
            </Box>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
      </ScrollArea.Root>
    </Box>
  );
}