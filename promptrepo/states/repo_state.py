import reflex as rx
from promptrepo.states.auth_state import AuthState
from github import Github, Auth
from typing import List, Any, Dict
import json

class Repo(rx.Base):
    id: int
    name: str
    selected: bool = False
    full_name: str
    html_url: str
    description: str | None = None
    private: bool

class RepoState(rx.State):
    repos: Dict[int, Repo] = {}
    selected_repo_ids_json: str = rx.LocalStorage("[]", sync=True)
    current_repo: str = ""

    @rx.event
    def set_current_repo(self, repo_name: str):
        self.current_repo = repo_name

    @rx.var
    def selected_repo_ids(self) -> list[int]:
        """The list of selected repository ids."""
        return json.loads(self.selected_repo_ids_json)

    @rx.var
    def all_repos(self) -> list[Repo]:
        """The list of all repositories."""
        return sorted(list(self.repos.values()), key=lambda r: r.name)

    @rx.var
    def selected_repos(self) -> list[Repo]:
        """The list of selected repositories."""
        return [repo for repo in self.all_repos if repo.id in self.selected_repo_ids]

    @rx.var
    def unselected_repos(self) -> list[Repo]:
        """The list of unselected repositories."""
        return [repo for repo in self.all_repos if repo.id not in self.selected_repo_ids]

    @rx.var
    def unselected_repo_names(self) -> list[str]:
        """The list of unselected repository names."""
        return [repo.name for repo in self.unselected_repos]

    @rx.event
    def add_repo(self, repo_name: str):
        """Add a repo to the selected list by name."""
        for repo in self.unselected_repos:
            if repo.name == repo_name:
                self.select_repo(repo.id)
                return

    @rx.event
    def select_repo(self, repo_id: int):
        """Toggle the selection of a repository."""
        selected_ids = self.selected_repo_ids
        self.repos[repo_id].selected = not self.repos[repo_id].selected
        if repo_id in selected_ids:
            selected_ids.remove(repo_id)
        else:
            selected_ids.append(repo_id)
        self.selected_repo_ids_json = json.dumps(selected_ids)

    @rx.event
    async def get_repos(self) -> None:
        """Fetch the list of repositories for the authenticated user."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.access_token:
            return
        if not self.repos:
            auth = Auth.Token(auth_state.access_token)
            git = Github(auth=auth)
            repos_map = {}
            selected_ids_set = set(self.selected_repo_ids)
            for repo in git.get_user().get_repos():
                repos_map[repo.id] = Repo(
                    id=repo.id,
                    name=repo.name,
                    selected=repo.id in selected_ids_set,
                    full_name=repo.full_name,
                    html_url=repo.html_url,
                    description=repo.description,
                    private=repo.private,
                )
            self.repos = repos_map
