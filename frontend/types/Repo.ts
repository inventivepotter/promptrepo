export interface Repo {
  id: string;
  name: string;
  full_name: string;
  owner: string;
  provider: string;
  branch: string;
  is_public: boolean;
}