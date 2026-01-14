"""
FastAPI backend application for PromptRepo.
"""
from fastapi import FastAPI, status
import logging
from contextlib import asynccontextmanager
import os

# Import database setup from the new architecture
from database.core import create_db_and_tables

# Import middleware
from middlewares import ContextMiddleware

# Import core setup and components from middlewares
from middlewares.rest.setup import setup_fastapi_app
from middlewares.rest.responses import StandardResponse, success_response
from services import remote_repo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API routers
from api.v0.auth import router as auth_router
from api.v0.llm import router as llm_router
from api.v0.config import router as config_router
from api.v0.repos import router as repos_router
from api.v0.health import router as health_router
from api.v0.info import router as info_router
from api.v0.prompts import router as prompts_router
from api.v0.tools import router as tools_router
from api.v0.evals import router as evals_router
from api.v0.promptimizer import router as promptimizer_router
from api.v0.shared_chats import router as shared_chats_router
from api.v0.conversational import router as conversational_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    logger.info("PromptRepo API started successfully")
    yield
    # Shutdown (if needed)
    logger.info("PromptRepo API shutting down")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Apply all best practices configuration using setup_fastapi_app
app = setup_fastapi_app(
    app,
    title="PromptRepo API",
    description="Backend API for PromptRepo application with GitHub OAuth",
    version="0.1.0",
    environment=os.getenv("ENVIRONMENT", "development")
)

# Add authentication middleware (after setup)
app.add_middleware(ContextMiddleware)

# Include API routers with versioning
app.include_router(
    auth_router,
    prefix="/api/v0/auth",
    tags=["authentication"]
)

app.include_router(
    llm_router,
    prefix="/api/v0/llm",
    tags=["llm"]
)

app.include_router(
    config_router,
    prefix="/api/v0/config",
    tags=["config"]
)

app.include_router(
    repos_router,
    prefix="/api/v0/repos",
    tags=["repos"]
)

app.include_router(
    info_router,
    prefix="/api/v0",
    tags=["info"]
)

app.include_router(
    prompts_router,
    prefix="/api/v0/prompts",
    tags=["prompts"]
)

app.include_router(
    tools_router,
    prefix="/api/v0/tools",
    tags=["tools"]
)

app.include_router(
    evals_router,
    prefix="/api/v0/evals",
    tags=["evals"]
)

app.include_router(
    promptimizer_router,
    prefix="/api/v0/promptimizer",
    tags=["promptimizer"]
)

app.include_router(
    shared_chats_router,
    prefix="/api/v0/shared-chats",
    tags=["shared-chats"]
)

app.include_router(
    conversational_router,
    prefix="/api/v0/conversational",
    tags=["conversational"]
)


@app.get("/", status_code=status.HTTP_307_TEMPORARY_REDIRECT, include_in_schema=False)
async def root_redirect():
    """
    Redirects the root path to the API info endpoint.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v0/info", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)