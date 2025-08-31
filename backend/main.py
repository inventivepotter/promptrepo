"""
FastAPI backend application for PromptRepo.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

# Import database setup
from models.database import create_db_and_tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API routers
from api.v0.auth import router as auth_router
from api.v0.llm import router as llm_router
from api.v0.config import router as config_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    logger.info("PromptRepo API started successfully")
    yield
    # Shutdown (if needed)
    logger.info("PromptRepo API shutting down")

# Create FastAPI app with lifespan
app = FastAPI(
    title="PromptRepo API",
    description="Backend API for PromptRepo application with GitHub OAuth",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Health check response model
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify the API is running.
    """
    return HealthResponse(
        status="healthy",
        message="PromptRepo API is running successfully",
        version="0.1.0"
    )


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint with basic API information.
    """
    routes = [
            "/api/v0/auth/login/github",
            "/api/v0/auth/callback/github",
            "/api/v0/auth/verify",
            "/api/v0/auth/logout",
            "/api/v0/auth/refresh",
            "/api/v0/llm/providers/available",
            "/api/v0/config",
            "/api/v0/config/export"
        ]
    return {
        "message": "Welcome to PromptRepo API",
        "version": "0.1.0",
        "docs": "/docs",
        "available_routes": " ".join(routes)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)