'use client';

import React, { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box } from '@chakra-ui/react';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { usePromptsState, Prompt } from '../_state/promptState';
import { PromptEditor } from '../_components/PromptEditor';
import { mockPrompts } from '../_lib/mockData';

export default function EditorPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const promptId = searchParams.get('id');
  
  // Theme colors
  const containerBg = useColorModeValue('gray.50', 'gray.800');

  const {
    promptsState,
    updatePrompt,
    setCurrentPrompt,
    currentPrompt,
  } = usePromptsState();

  // Initialize with mock data if no prompts exist
  useEffect(() => {
    if (promptsState.prompts.length === 0 && typeof window !== 'undefined') {
      const existingData = localStorage.getItem('promptsData');
      if (!existingData) {
        // Only set mock data if there's nothing in localStorage
        localStorage.setItem('promptsData', JSON.stringify(mockPrompts));
        // Force refresh only once
        window.location.reload();
      }
    }
  }, [promptsState.prompts.length]);

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

  const handleSave = (updates: Partial<Prompt>) => {
    if (currentPrompt) {
      updatePrompt(currentPrompt.id, updates);
      // Optionally show a success message or redirect
      //router.push('/prompts');
    }
  };

  const handleBack = () => {
    router.push('/prompts');
  };

  return (
    <Box minH="100vh" bg={containerBg}>
      <PromptEditor
        prompt={currentPrompt}
        onSave={handleSave}
        onBack={handleBack}
      />
    </Box>
  );
}