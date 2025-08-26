import { SelectedRepo } from './repository';

export interface Prompt {
  id: string;
  name: string;
  description: string;
  prompt: string;
  model: string;
  failover_model: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
  thinking_enabled: boolean;
  thinking_budget: number;
  repo?: SelectedRepo;
  created_at: Date;
  updated_at: Date;
}

export interface PromptsState {
  prompts: Prompt[];
  currentPrompt: Prompt | null;
  searchQuery: string;
  currentPage: number;
  itemsPerPage: number;
  sortBy: 'name' | 'updated_at';
  sortOrder: 'asc' | 'desc';
  selectedRepos: Array<SelectedRepo>;
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