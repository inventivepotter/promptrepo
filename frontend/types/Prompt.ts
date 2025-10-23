import { components } from '@/types/generated/api';

export type CommitInfo = components['schemas']['CommitInfo'];
// Search parameters
export interface PromptSearchParams {
  query?: string;
  repo_name?: string;
  tags?: string[];
  owner?: string;
  page?: number;
  page_size?: number;
}
