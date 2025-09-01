import { Repo } from "./Repo";

export interface CommitInfo {
  hash: string;
  message: string;
  author: string;
  date: string;
}

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
  repo?: Repo;
  created_at: Date;
  updated_at: Date;
  recent_commits?: CommitInfo[];
}
