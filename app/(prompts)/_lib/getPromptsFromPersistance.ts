import { Prompt, PromptJson } from '../_types/state';
import prompts from './prompts.json';

export function getPromptsFromPersistance(): Prompt[] {
  return (prompts as PromptJson[]).map((p) => ({
    ...p,
    created_at: new Date(p.created_at),
    updated_at: new Date(p.updated_at),
  }));
}
