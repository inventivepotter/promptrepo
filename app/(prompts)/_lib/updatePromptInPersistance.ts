import type { Prompt } from '@/types/Prompt';

export async function updatePromptInPersistance(updates: Partial<Prompt>) {
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return { success: true };
}