import { Repo } from "../_components/RepoStep";


export function getReposNBranches(): Repo[] {
  return [
    { id: 1, name: 'my-project', fullName: 'user/my-project', branches: ['main', 'develop', 'feature/auth'] },
    { id: 2, name: 'web-app', fullName: 'user/web-app', branches: ['main', 'staging'] },
    { id: 3, name: 'api-server', fullName: 'user/api-server', branches: ['main', 'v2', 'hotfix'] }
  ];
}
