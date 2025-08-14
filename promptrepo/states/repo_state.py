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
    local_repo_branches: dict[str, list[str]] = {}
    selected_branch: dict[str, str] = {}

    @rx.event
    def fetch_local_repo_branches(self, repo_name: str):
        """Fetch available branches for a local repo."""
        repo_path = os.path.join("repos", repo_name)
        try:
            repo = GitRepo(repo_path)
            branches = [h.name for h in repo.heads]
            self.local_repo_branches[repo_name] = branches
            # Default to current branch if not set
            if repo_name not in self.selected_branch and branches:
                self.selected_branch[repo_name] = repo.active_branch.name
        except Exception:
            self.local_repo_branches[repo_name] = []
            self.selected_branch[repo_name] = ""

    @rx.event
    def set_selected_branch(self, repo_name: str, branch: str):
        """Set the selected branch for a repo."""
        self.selected_branch[repo_name] = branch

    @rx.event
    def checkout_local_repo_branch(self, repo_name: str):
        """Checkout the selected branch for a local repo."""
        repo_path = os.path.join("repos", repo_name)
        branch = self.selected_branch.get(repo_name, "")
        try:
            repo = GitRepo(repo_path)
            repo.git.checkout(branch)
            # Refresh branches and selected branch
            self.fetch_local_repo_branches(repo_name)
        except Exception:
            pass

    @rx.event
    def refresh_local_repos(self):
        """Refresh the list of local repo directories in the repos folder."""
        repos_path = os.path.join("repos")
        try:
            self.local_repos = [
                name for name in os.listdir(repos_path)
                if os.path.isdir(os.path.join(repos_path, name))
            ]
        except Exception:
            self.local_repos = []
        # Fetch branches for each repo
        for name in self.local_repos:
            self.fetch_local_repo_branches(name)

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
            local_repo_set = set(self.local_repos)
            for repo in git.get_user().get_repos():
                # Mark selected if either selected_ids or exists locally
                is_selected = repo.id in selected_ids_set or repo.name in local_repo_set
                repos_map[repo.id] = Repo(
                    id=repo.id,
                    name=repo.name,
                    selected=is_selected,
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
