import reflex as rx
from promptrepo.states.auth_state import AuthState
from github import Github, Auth

from typing import List, Dict, Any

class RepoState(rx.State):
    repos: List[Dict[str, Any]] = []
    selected_repos: List[Dict[str, Any]] = []
    current_repo: str = ""

    @rx.event
    def set_current_repo(self, repo_name: str):
        self.current_repo = repo_name

    @rx.var
    def selected_repo_names(self) -> list[str]:
        return [r["full_name"] for r in self.selected_repos]

    def is_repo_selected(self, repo: Dict[str, Any]) -> bool:
        """Check if a repository is selected."""
        return any(r["id"] == repo["id"] for r in self.selected_repos)

    @rx.event
    def select_repo(self, repo: Dict[str, Any]):
        """Toggle the selection of a repository."""
        repo_id = repo["id"]
        if any(r["id"] == repo_id for r in self.selected_repos):
            self.selected_repos = [r for r in self.selected_repos if r["id"] != repo_id]
        else:
            self.selected_repos.append(repo)

    @rx.event
    async def get_repos(self) -> None:
        """Fetch the list of repositories for the authenticated user."""
        auth_state = await self.get_state(AuthState)
        if auth_state.access_token:
            auth = Auth.Token(auth_state.access_token)
            git = Github(auth=auth)
            repos_list = []
            for repo in git.get_user().get_repos():
                repos_list.append(
                    {
                        "id": repo.id,
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "url": repo.html_url,
                        "description": repo.description,
                        "private": repo.private,
                    }
                )
            self.repos = repos_list