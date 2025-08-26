'use client';

import React, { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box } from '@chakra-ui/react';
import { Prompt } from '@/types/Prompt';
import { usePromptsState } from '../_state/promptState';
import { PromptEditor } from '../_components/PromptEditor';
import { updatePromptInPersistance } from '../_lib/updatePromptInPersistance';

export default function EditorPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptId = searchParams.get('id');
  

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
      updatePrompt(currentPrompt.id, updates);
      await updatePromptInPersistance(updates);
      // Optionally show a success message or redirect
      //router.push('/prompts');
    }
  };

  const handleBack = () => {
    router.push('/prompts');
  };

  return (
    <Box minH="100vh">
      <PromptEditor
        prompt={currentPrompt}
        onSave={handleSave}
        onBack={handleBack}
        selectedRepos={promptsState.selectedRepos}
      />
    </Box>
  );
}