# backend/api/v0/repos.py
"""
API endpoints for managing user repositories.
Handles repository cloning, status tracking, and management operations.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import Session, select
from typing import List, Optional
import logging



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
from utils.auth_utils import verify_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/available", response_model=AvailableReposResponse)
async def get_available_repositories(
    username: str = Depends(verify_session),
    db: Session = Depends(get_session)
):
    pass


@router.get("/configured", response_model=ConfiguredReposResponse)
async def get_configured_repositories(
    username: str = Depends(verify_session),
    db: Session = Depends(get_session)
):
    pass