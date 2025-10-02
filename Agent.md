# Instructions
* This project is a monorepo project with frontend, backend directories
* Frontend is Next.js app
* Backend is Python
* Make sure to use strict design patterns and SOLID priniciples building features
* Don't assume anything when coming to docs, always refer to context7 MCP for docs
* Always cleanup the code by removing unused imports

# Backend
* Backend is a python app that uses FastAPI
* Use pydantic models every where possible
* Keep files atomic that just does one thing
* Use uv as package manager, use `uv sync`
* Always add unit tests, run unit tests using  `uv run pytest`. Don't create a lot of tests but create quality tests that cover all scenarios.
* Keep controllers/handlers under api/v0/* light, they should just validate and pass on the logic to service.
* Services should only handle business logic but nothing else. Any dendencies needed for service should follow "Constructor injection" pattern.
* All dependency injection is centralized in backend/api/deps.py - use type aliases like DBSession, ConfigServiceDep instead of Depends() directly.
* Don't start imports from `` always consider backend folder is root for python project and start imports from within backend directory.
* **API Endpoints Standard Pattern**: All API endpoints should follow the standardized response pattern (see `backend/api/v0/config/` for reference):
  - Use `response_model=StandardResponse[DataType]` in route decorators
  - Include explicit `status_code=status.HTTP_XXX`
  - Add `summary` and `description` for OpenAPI documentation
  - Include `responses` parameter for error case documentation
  - Add return type annotations on handler functions
  - Raise exceptions (`AppException`, `ValidationException`, `NotFoundException`, etc.) instead of manually returning `error_response()`
  - Let global exception handlers deal with exceptions
  - Include `Request` parameter to access `request_id` for logging
  - Add structured logging with `request_id` and `user_id`

# Frontend