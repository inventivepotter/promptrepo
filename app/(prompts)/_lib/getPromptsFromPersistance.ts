import { Prompt } from '../_state/promptState';
import prompts from './prompts.json';

type PromptJson = Omit<Prompt, 'created_at' | 'updated_at'> & {
  created_at: string;
  updated_at: string;
};

export function getPromptsFromPersistance(): Prompt[] {
  return (prompts as PromptJson[]).map((p) => ({
    ...p,
    created_at: new Date(p.created_at),
    updated_at: new Date(p.updated_at),
  }));
}
