import { Repo } from "@/types/Repo";


export function getReposNBranches(): Repo[] {
  return [
    { id: '1', name: 'frontend', all_branches: ['main'] },
    { id: '2', name: 'backend', all_branches: ['develop'] },
    { id: '3', name: 'database', all_branches: ['main'] },
    { id: '4', name: 'api-server', all_branches: ['main'] },
    { id: '5', name: 'web-app', all_branches: ['main'] }
  ];
}
