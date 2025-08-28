"""
FastAPI backend application for PromptRepo.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="PromptRepo API",
    description="Backend API for PromptRepo application",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7376"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {
        "message": "Welcome to PromptRepo API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7768)