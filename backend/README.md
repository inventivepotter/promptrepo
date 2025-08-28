# PromptRepo Backend

FastAPI backend application for PromptRepo.

## Development Setup

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Install development dependencies:
```bash
uv sync --extra dev
```

### Running the Application

#### Development Server
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Server
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Direct Python Execution
```bash
uv run python main.py
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Check

Check if the API is running:
```bash
curl http://localhost:8000/health
```

### Code Quality

Format code:
```bash
uv run black .
uv run isort .
```

Type checking:
```bash
uv run mypy .
```

Run tests:
```bash
uv run pytest
```

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)