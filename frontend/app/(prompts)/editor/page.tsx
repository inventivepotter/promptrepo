'use client';

import React, { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box } from '@chakra-ui/react';
import { Prompt } from '@/types/Prompt';
import { usePromptsState } from "../_state/promptState";
import { PromptEditor } from '../_components/PromptEditor';
import { promptsService } from '@/services/prompts';
import { LoadingOverlay } from '@/components/LoadingOverlay';

function EditorPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptId = searchParams.get('id');
  const [isSaving, setIsSaving] = useState(false);
  const fetchingRef = useRef<string | null>(null);

  const {
    promptsState,
    updatePrompt,
    setCurrentPrompt,
    currentPrompt,
  } = usePromptsState();

  // Fetch and set the current prompt with commit history based on the ID from URL
  useEffect(() => {
    // Prevent duplicate requests for the same prompt ID
    if (promptId && fetchingRef.current !== promptId) {
      fetchingRef.current = promptId;
      
      const fetchPrompt = async () => {
        try {
          const prompt = await promptsService.getPrompt(promptId);
          // Only update state if we're still fetching this prompt ID
          if (fetchingRef.current === promptId) {
            if (prompt) {
              setCurrentPrompt(prompt);
            } else {
              // Prompt not found, redirect to prompts list
              router.push('/prompts');
            }
          }
        } finally {
          // Clear the fetching reference only if it's still for this prompt ID
          if (fetchingRef.current === promptId) {
            fetchingRef.current = null;
          }
        }
      };
      
      fetchPrompt();
    } else if (!promptId) {
      // No ID provided, redirect to prompts list
      router.push('/prompts');
    }
  }, [promptId, setCurrentPrompt, router]);

  const handleSave = async (updates: Partial<Prompt>) => {
    if (currentPrompt) {
      setIsSaving(true);
      try {
        // Ensure the updates object includes the ID
        const updatesWithId = { ...updates, id: currentPrompt.id };
        
        // First try to save to backend
        await promptsService.updatePrompt(updatesWithId);
        // Only update localStorage if backend save was successful
        updatePrompt(currentPrompt.id, updatesWithId);
      } catch (error) {
        // Handle error (could add toast notification here)
      } finally {
        setIsSaving(false);
      }
    }
  };

  const handleBack = () => {
    router.push('/prompts');
  };

  return (
    <>
      <LoadingOverlay
        isVisible={isSaving}
        title="Saving Prompt..."
        subtitle="Please wait while we save your changes"
      />
      <Box minH="100vh">
        <PromptEditor
          prompt={currentPrompt}
          onSave={handleSave}
          onBack={handleBack}
          configuredRepos={promptsState.configuredRepos}
          configuredModels={promptsState.configuredModels}
          isSaving={isSaving}
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