import { Prompt } from '@/types/Prompt';
import { Repo } from "@/types/Repo";

export interface PromptsState {
  prompts: Prompt[];
  currentPrompt: Prompt | null;
  searchQuery: string;
  currentPage: number;
  itemsPerPage: number;
  sortBy: 'name' | 'updated_at';
  sortOrder: 'asc' | 'desc';
  configuredRepos: Array<Repo>;
  repoFilter: string;
  currentRepoStep: {
    isLoggedIn: boolean;
    selectedRepo: string;
    selectedBranch: string;
  };
}

export type PromptJson = Omit<Prompt, 'created_at' | 'updated_at'> & {
  created_at: string;
  updated_at: string;
};