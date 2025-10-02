'use client';

import { useEffect, useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  ScrollArea,
} from '@chakra-ui/react';
import { Prompt } from '@/types/Prompt';
import { Repo } from '@/types/Repo';
import { PromptEditorHeader } from './PromptEditorHeader';
import { PromptFieldGroup } from './PromptFieldGroup';
import { Chat } from './Chat';
import { PromptTimeline } from './PromptTimeline';
import { useUser } from '@/stores/authStore';
import { usePromptActions, useFormData, useShowRepoError, useHasUnsavedChanges, useFormActions } from '@/stores/promptStore/hooks';


interface PromptEditorProps {
  prompt: Prompt | null;
  onSave: (updates: Partial<Prompt>) => void;
  onBack: () => void;
  configuredRepos?: Array<Repo>;
  isSaving?: boolean;
}

export function PromptEditor({ prompt, onSave, onBack, configuredRepos = [], isSaving = false }: PromptEditorProps) {
  const { setCurrentPrompt } = usePromptActions();
  const formData = useFormData();
  const showRepoError = useShowRepoError();
  const hasUnsavedChanges = useHasUnsavedChanges();
  const { initializeForm, updateFormField, updateFormRepo, setShowRepoError } = useFormActions();

  // Initialize form data when prompt changes
  useEffect(() => {
    initializeForm(prompt);
    // Update store with current prompt
    setCurrentPrompt(prompt);
  }, [prompt, initializeForm, setCurrentPrompt]);

  const updateField = (field: keyof Prompt, value: string | number | boolean) => {
    // Check if repository is selected before allowing other field edits
    if (!formData.repo && !showRepoError) {
      setShowRepoError(true);
      return;
    }
    
    updateFormField(field as keyof typeof formData, value as string);
  };

  const updateRepoField = (repo: Repo | undefined) => {
    updateFormRepo(repo);
  };

  const handleSave = () => {
    if (!formData.repo) {
      setShowRepoError(true);
      return;
    }
    onSave(formData);
    // Note: originalFormData is updated in the store after successful save
  };

  const user = useUser();

  // Get commits from prompt data with 0th commit for latest changes
  const commits = useMemo(() => {
    const draftCommit = {
      commit_id: '0',
      message: '',
      author: user?.oauth_name || user?.oauth_username || 'Unknown User',
      timestamp: new Date().toISOString(),
      isLatest: true
    };

    if (prompt?.recent_commits && prompt.recent_commits.length > 0) {
      // Add the draft commit at position 0, then the API commits
      return [
        draftCommit,
        ...prompt.recent_commits.map((commit) => ({
          ...commit,
          isLatest: false
        }))
      ];
    }
    
    // Return just the draft commit if no API commits available
    return [draftCommit];
  }, [prompt?.recent_commits, user?.oauth_name, user?.oauth_username]);

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Sticky Header - Outside ScrollArea */}
      <PromptEditorHeader
        onBack={onBack}
        onSave={handleSave}
        canSave={!!formData.repo && hasUnsavedChanges}
        isSaving={isSaving}
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
                    p={6}
                    borderWidth="1px"
                    borderRadius="md"
                    borderColor="border.muted"
                    width="54%"
                  >
                    <VStack gap={6} align="stretch">
                      {/* Basic Info */}
                      <PromptFieldGroup
                        formData={formData}
                        configuredRepos={configuredRepos}
                        showRepoError={showRepoError}
                        updateField={updateField}
                        updateRepoField={updateRepoField}
                      />
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