import { Repo } from "../_types/repository";


export function getReposNBranches(): Repo[] {
  return [
    { id: 1, name: 'frontend', branches: ['main'] },
    { id: 2, name: 'backend', branches: ['develop'] },
    { id: 3, name: 'database', branches: ['main'] },
    { id: 4, name: 'api-server', branches: ['main'] },
    { id: 5, name: 'web-app', branches: ['main'] }
  ];
}
