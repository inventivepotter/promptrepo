import type { Prompt } from '@/types/Prompt';

export async function updatePromptInPersistance(updates: Partial<Prompt>) {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return { success: true };
}