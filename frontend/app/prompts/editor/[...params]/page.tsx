'use client';

import React, { useEffect, Suspense } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { usePromptActions } from '@/stores/promptStore';
import { PromptEditor } from '../../_components/PromptEditor';
import { LoadingOverlay } from '@/components/LoadingOverlay';
import { decodeBase64Url } from '@/lib/urlEncoder';

function EditorPageContent() {
  const router = useRouter();
  const params = useParams();
  
  const {
    fetchPromptById,
    clearCurrentPrompt,
    setCurrentPrompt,
  } = usePromptActions();

  // Fetch and set the current prompt based on URL path params
  useEffect(() => {
    // Parse path-based routing: /editor/{base64_repo}/{base64_file}
    const pathParams = params.params as string[];
    
    if (!pathParams || pathParams.length < 2) {
      // Invalid path, redirect to prompts list
      router.push('/prompts');
      return;
    }
    
    try {
      const repositoryName = decodeBase64Url(pathParams[0]);
      
      // Check if it's 'new' mode
      if (pathParams[1] === 'new') {
        // New prompt mode
        setCurrentPrompt({
          repo_name: repositoryName,
          file_path: '',
          prompt: {
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
      } else {
        // Editing an existing prompt
        const filePath = decodeBase64Url(pathParams[1]);
        fetchPromptById(repositoryName, filePath);
      }
    } catch (error) {
      console.error('Failed to decode path parameters:', error);
      router.push('/prompts');
    }
    
    // Clear current prompt when unmounting
    return () => {
      clearCurrentPrompt();
    };
  }, [params, fetchPromptById, clearCurrentPrompt, setCurrentPrompt, router]);

  return <PromptEditor />;
}

export default function EditorPage() {
  return (
    <Suspense fallback={<LoadingOverlay isVisible={true} title="Loading..." subtitle="Loading page data" />}>
      <EditorPageContent />
    </Suspense>
  );
}