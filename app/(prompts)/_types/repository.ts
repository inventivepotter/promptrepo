export interface Repo {
  id: number;
  name: string;
  branches: string[];
}

export interface SelectedRepo {
  id: number;
  name: string;
  branch: string;
}