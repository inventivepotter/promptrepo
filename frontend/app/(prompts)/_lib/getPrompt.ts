import { Prompt, CommitInfo } from '@/types/Prompt';
import { PromptJson } from '../_types/PromptState';
import { promptsApi } from './api/promptsApi';
import { errorNotification } from '@/lib/notifications';
import prompts from './prompts.json';

/**
 * Generate mock commit history for a prompt
 */
function generateMockCommitHistory(): CommitInfo[] {
  const mockCommits: CommitInfo[] = [
    {
      hash: "a1b2c3d",
      message: "Update prompt parameters and improve clarity",
      author: "John Doe",
      date: "2024-03-14T10:30:00Z"
    },
    {
      hash: "e4f5g6h",
      message: "Fix typo in prompt description",
      author: "Jane Smith",
      date: "2024-03-12T15:45:00Z"
    },
    {
      hash: "i7j8k9l",
      message: "Add thinking_enabled parameter",
      author: "Bob Wilson",
      date: "2024-03-10T09:15:00Z"
    },
    {
      hash: "m0n1o2p",
      message: "Initial prompt creation",
      author: "Alice Johnson",
      date: "2024-03-08T14:20:00Z"
    }
  ];
  
  return mockCommits;
}

/**
 * Get mock prompt by ID from local data
 */
function getMockPromptById(id: string): Prompt | null {
  const promptJson = (prompts as PromptJson[]).find(p => p.id === id);
  
  if (!promptJson) {
    return null;
  }

  return {
    ...promptJson,
    created_at: new Date(promptJson.created_at),
    updated_at: new Date(promptJson.updated_at),
    recent_commits: generateMockCommitHistory()
  };
}

/**
 * Get individual prompt with commit history
 * Handles error notifications and fallback to mock data
 */
export async function getPrompt(id: string): Promise<Prompt | null> {
  try {
    const result = await promptsApi.getPrompt(id);
    
    if (!result.success) {
      // Show user-friendly notification and fall back to mock data
      errorNotification(
        result.error || 'Failed to Load Prompt',
        result.message || 'Unable to load prompt from server. Using local data.'
      );
      return getMockPromptById(id);
    }

    if (!result.data) {
      errorNotification(
        'Prompt Not Found',
        'The requested prompt could not be found on server. Using local data.'
      );
      return getMockPromptById(id);
    }

    // Convert date strings to Date objects
    const data = {
      ...result.data,
      created_at: new Date(result.data.created_at),
      updated_at: new Date(result.data.updated_at)
    };
    
    return data;
  } catch (error: unknown) {
    console.error('Error fetching prompt:', error);
    errorNotification(
      'Connection Error',
      'Unable to connect to prompt service. Using local data.'
    );
    return getMockPromptById(id);
  }
}