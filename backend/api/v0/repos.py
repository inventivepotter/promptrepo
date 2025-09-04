# backend/api/v0/repos.py
"""
API endpoints for managing user repositories.
Handles repository cloning, status tracking, and management operations.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from sqlmodel import Session, select
from typing import List, Optional
import logging


from settings.base_settings import Settings
# Database and models
from models.database import get_session
from models.user_sessions import User
from models.user_repos import UserRepos, RepoStatus

from services.user_repos_service import UserReposService
from services.session_service import SessionService

# Schemas
from schemas.user_repos import (
    AddRepositoryRequest,
    UpdateRepositoryStatusRequest,
    UserRepositoryResponse,
    UserRepositoriesResponse,
    UserRepositoriesSummaryResponse,
    RepositoryStatusSummary,
    SuccessResponse,
    ErrorResponse
)
from services.repo_locator_service import create_repo_locator
from utils.auth_utils import verify_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/available")
async def get_available_repositories(request: Request
):
    repos = None
    hosting_type = Settings.app_config.hosting_type
    if hosting_type == "individual":
        repos = create_repo_locator(hosting_type)
    elif hosting_type == "organization":
        authorization_header = request.headers.get("Authorization")
        session_id = authorization_header.replace("Bearer ", "") if authorization_header else None
        db = get_session()
        if SessionService.is_session_valid(db, session_id):
            data = SessionService.get_oauth_token_and_username(db, session_id)
            if data:
                repos = create_repo_locator(hosting_type, oauth_token=data['oauth_token'], username=data['username'])
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session not found"
                )
    return {"repos":repos}
@router.get("/configured", response_model=ConfiguredReposResponse)
async def get_configured_repositories(
    username: str = Depends(verify_session),
    db: Session = Depends(get_session)
):
    pass