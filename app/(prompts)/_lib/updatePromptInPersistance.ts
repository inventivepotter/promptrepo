import type { Prompt } from "../_types/state";

export async function updatePromptInPersistance(updates: Partial<Prompt>) {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return { success: true };
}