export interface User {
  id: string;
  username: string;
  name: string;
  email: string;
  avatar_url: string;
  github_id: string | null;
  html_url: string | null;
  sessions: unknown;
}
