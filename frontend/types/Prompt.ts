import { Repo } from "./Repo";

export interface CommitInfo {
  hash: string;
  message: string;
  author: string;
  date: string;
}

// Backend Prompt model fields
export interface Prompt {
  id: string;
  name: string;
  description: string | null;
  content: string; // Full prompt content (JSON format)
  repo_name: string;
  file_path: string;
  category: string | null;
  tags: string[];
  system_prompt: string | null;
  user_prompt: string | null;
  owner: string | null;
  created_at: string; // ISO date string from backend
  updated_at: string; // ISO date string from backend
  
  // Optional frontend-specific fields
  repo?: Repo;
  recent_commits?: CommitInfo[];
}

// Request models matching backend
export interface PromptCreate {
  name: string;
  description?: string | null;
  repo_name: string;
  file_path: string;
  category?: string | null;
  tags?: string[];
  system_prompt?: string | null;
  user_prompt?: string | null;
  metadata?: Record<string, any>;
}

export interface PromptUpdate {
  name?: string;
  description?: string | null;
  category?: string | null;
  tags?: string[];
  system_prompt?: string | null;
  user_prompt?: string | null;
  metadata?: Record<string, any>;
}

// Response models for list operations
export interface PromptListResponse {
  prompts: Prompt[];
  total: number;
  page: number;
  page_size: number;
}

// Search parameters
export interface PromptSearchParams {
  query?: string;
  repo_name?: string;
  category?: string;
  tags?: string[];
  owner?: string;
  page?: number;
  page_size?: number;
}
