"""
Example of how to use the new FastAPI best practices setup.
This shows how to integrate the standardized response format and setup.
"""
from fastapi import FastAPI, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os

# Import database setup
from models.database import create_db_and_tables

# Import middleware  
from middlewares import AuthMiddleware

# Import core setup and components
from middlewares.rest import.setup import setup_fastapi_app
from middlewares.rest import.responses import StandardResponse, success_response
from middlewares.rest import.exceptions import NotFoundException

# Import API routers
from api.v0.auth import router as auth_router
from api.v0.llm import router as llm_router
from api.v0.config import router as config_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown


# Step 1: Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Step 2: Apply all best practices configuration
app = setup_fastapi_app(
    app,
    title="PromptRepo API",
    description="Backend API for PromptRepo application with standardized responses",
    version="1.0.0",
    environment=os.getenv("ENVIRONMENT", "development")
)

# Step 3: Add your custom middleware (after setup)
app.add_middleware(AuthMiddleware)

# Step 4: Include routers
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


# Step 5: Define your endpoints with standardized responses

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str
    version: str
    environment: str


@app.get(
    "/health",
    response_model=StandardResponse[HealthResponse],
    status_code=status.HTTP_200_OK,
    tags=["monitoring"],
    summary="Health check",
    description="Check if the API is running and healthy",
)
async def health_check() -> StandardResponse[HealthResponse]:
    """
    Health check endpoint with standardized response.
    """
    health_data = HealthResponse(
        status="healthy",
        message="PromptRepo API is running successfully",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )
    
    return success_response(
        data=health_data,
        message="Service is healthy"
    )


class APIInfo(BaseModel):
    """API information model."""
    name: str
    version: str
    description: str
    documentation: dict
    endpoints: dict


@app.get(
    "/",
    response_model=StandardResponse[APIInfo],
    status_code=status.HTTP_200_OK,
    tags=["info"],
    summary="API information",
    description="Get basic information about the API",
)
async def root() -> StandardResponse[APIInfo]:
    """
    Root endpoint with standardized API information.
    """
    api_info = APIInfo(
        name="PromptRepo API",
        version="1.0.0",
        description="Backend API for PromptRepo application",
        documentation={
            "openapi": "/openapi.json",
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        endpoints={
            "health": "/health",
            "auth": "/api/v0/auth",
            "config": "/api/v0/config",
            "llm": "/api/v0/llm"
        }
    )
    
    return success_response(
        data=api_info,
        message="Welcome to PromptRepo API"
    )


# Example of using custom exceptions
@app.get(
    "/example/{item_id}",
    response_model=StandardResponse[dict],
    tags=["info"],
)
async def get_example(item_id: int) -> StandardResponse[dict]:
    """
    Example endpoint showing exception handling.
    """
    if item_id == 404:
        raise NotFoundException(
            resource="Example",
            identifier=str(item_id)
        )
    
    return success_response(
        data={"id": item_id, "name": f"Example {item_id}"},
        message="Example retrieved successfully"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)