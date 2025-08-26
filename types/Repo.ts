
export interface Repo {
  id: string;
  name: string;
  prompts_directory?: string;
  base_branch?: string;
  current_branch?: string;
  remote_url?: string;
  all_branches?: string[];
}
