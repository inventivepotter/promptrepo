import reflex as rx
from promptrepo.states.auth_state import AuthState
from github import Github, Auth
from typing import List, Any, Dict
import json
from git import Repo as GitRepo
import shutil
import os

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
    local_repos: list[str] = []

    @rx.event
    def refresh_local_repos(self):
        """Refresh the list of local repo directories in the repos folder."""
        repos_path = os.path.join(os.path.dirname(__file__), "..", "..", "repos")
        try:
            self.local_repos = [
                name for name in os.listdir(repos_path)
                if os.path.isdir(os.path.join(repos_path, name))
            ]
        except Exception:
            self.local_repos = []

    async def get_auth_token(self) -> str | None:
        """Retrieve the GitHub auth token from AuthState."""
        auth_state = await self.get_state(AuthState)
        if not getattr(auth_state, "access_token", None):
            return None
        return auth_state.access_token

    @rx.var
    async def authenticated_git(self) -> Github | None:
        """Return an authenticated Github client using the user's token."""
        git_auth_token = await self.get_auth_token()
        if not git_auth_token:
            return None
        auth_token = Auth.Token(git_auth_token)
        git = Github(auth=auth_token)
        return git

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
    async def add_repo(self, repo_name: str):
        """Add a repo to the selected list by name."""
        for repo in self.unselected_repos:
            if repo.name == repo_name:
                await self.select_repo(repo.id)
                return

    @rx.event
    async def select_repo(self, repo_id: int):
        """Toggle the selection of a repository."""
        selected_ids = self.selected_repo_ids
        self.repos[repo_id].selected = not self.repos[repo_id].selected
        if repo_id in selected_ids:
            self.remove_repo(repo_id)
            selected_ids.remove(repo_id)
        else:
            await self.clone_repo(self.repos[repo_id], f"repos/{self.repos[repo_id].name}")
            selected_ids.append(repo_id)
        self.selected_repo_ids_json = json.dumps(selected_ids)
        self.refresh_local_repos()

    @rx.event
    async def get_repos(self) -> None:
        """Fetch the list of repositories for the authenticated user."""
        git = await self.authenticated_git
        if not self.repos and git:
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

    async def clone_repo(self, repo: Repo, destination: str) -> None:
        """Clone the given repository to the specified destination."""
        git = await self.authenticated_git
        if git:
            git_auth_token = await self.get_auth_token()
            if not git_auth_token:
                return
            GitRepo.clone_from(
                f"https://github.com/{repo.full_name}.git",
                destination,
                env={"GIT_AUTH_TOKEN": git_auth_token}
            )

    def remove_repo(self, repo_id: int) -> None:
        """Remove the cloned repository from local storage."""
        repo = self.repos.get(repo_id)
        if repo:
            repo_path = f"repos/{repo.name}"
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
        self.refresh_local_repos()
