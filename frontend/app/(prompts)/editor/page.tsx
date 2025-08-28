'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box } from '@chakra-ui/react';
import { Prompt } from '@/types/Prompt';
import { usePromptsState } from "../_state/promptState";
import { PromptEditor } from '../_components/PromptEditor';
import { updatePrompt as updatePromptBackend } from '../_lib/updatePrompt';
import { LoadingOverlay } from '@/components/LoadingOverlay';

function EditorPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptId = searchParams.get('id');
  const [isSaving, setIsSaving] = useState(false);

  const {
    promptsState,
    updatePrompt,
    setCurrentPrompt,
    currentPrompt,
  } = usePromptsState();

  // Find and set the current prompt based on the ID from URL
  useEffect(() => {
    if (promptId && promptsState.prompts.length > 0) {
      const prompt = promptsState.prompts.find(p => p.id === promptId);
      if (prompt) {
        setCurrentPrompt(prompt);
      } else {
        // Prompt not found, redirect to prompts list
        router.push('/prompts');
      }
    } else if (!promptId) {
      // No ID provided, redirect to prompts list
      router.push('/prompts');
    }
  }, [promptId, promptsState.prompts, setCurrentPrompt, router]);

  const handleSave = async (updates: Partial<Prompt>) => {
    if (currentPrompt) {
      setIsSaving(true);
      try {
        // Ensure the updates object includes the ID
        const updatesWithId = { ...updates, id: currentPrompt.id };
        
        // First try to save to backend
        await updatePromptBackend(updatesWithId);
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