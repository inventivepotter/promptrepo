'use client';

import React, { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { usePromptActions } from '@/stores/promptStore';
import { PromptEditor } from '../_components/PromptEditor';
import { LoadingOverlay } from '@/components/LoadingOverlay';

function EditorPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const repoName = searchParams.get('repo_name');
  const filePath = searchParams.get('file_path');
  
  const {
    fetchPromptById,
    clearCurrentPrompt,
  } = usePromptActions();

  // Fetch and set the current prompt based on repo_name and file_path from URL
  useEffect(() => {
    if (repoName && filePath) {
      fetchPromptById(repoName, filePath);
    } else {
      // No repo/file provided, redirect to prompts list
      router.push('/prompts');
    }
    
    // Clear current prompt when unmounting
    return () => {
      clearCurrentPrompt();
    };
  }, [repoName, filePath, fetchPromptById, clearCurrentPrompt, router]);

  return <PromptEditor />;
}

export default function EditorPage() {
  return (
    <Suspense fallback={<LoadingOverlay isVisible={true} title="Loading..." subtitle="Loading page data" />}>
      <EditorPageContent />
    </Suspense>
  );
}