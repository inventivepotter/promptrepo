'use client';

import React, { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { usePromptActions } from '@/stores/promptStore';
import { PromptEditor } from '../_components/PromptEditor';
import { LoadingOverlay } from '@/components/LoadingOverlay';

function EditorPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mode = searchParams.get('mode');
  const repo = searchParams.get('repo');
  const repoName = searchParams.get('repo_name');
  const filePath = searchParams.get('file_path');
  
  const {
    fetchPromptById,
    clearCurrentPrompt,
    setCurrentPrompt,
  } = usePromptActions();

  // Fetch and set the current prompt based on mode and URL params
  useEffect(() => {
    // Support both 'repo' and 'repo_name' params for backward compatibility
    const repositoryName = repoName || repo;
    
    if (mode === 'new' && repositoryName) {
      // Creating a new prompt - set up an empty prompt
      setCurrentPrompt({
        repo_name: repositoryName,
        file_path: '', // Will be derived from prompt name when saving
        prompt: {
          id: '',
          name: 'Untitled Prompt',
          description: '',
          provider: '',
          model: '',
          prompt: '',
          tags: [],
          temperature: 0.05,
          top_p: 0.95,
          reasoning_effort: 'auto',
        },
      });
    } else if (repoName && filePath) {
      // Editing an existing prompt
      fetchPromptById(repoName, filePath);
    } else {
      // No valid params provided, redirect to prompts list
      router.push('/prompts');
    }
    
    // Clear current prompt when unmounting
    return () => {
      clearCurrentPrompt();
    };
  }, [mode, repo, repoName, filePath, fetchPromptById, clearCurrentPrompt, setCurrentPrompt, router]);

  return <PromptEditor />;
}

export default function EditorPage() {
  return (
    <Suspense fallback={<LoadingOverlay isVisible={true} title="Loading..." subtitle="Loading page data" />}>
      <EditorPageContent />
    </Suspense>
  );
}