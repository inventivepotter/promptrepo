# Instructions
* This project is a monorepo project with frontend, backend directories
* Frontend is Next.js app
* Backend is Python
* Make sure to use strict design patterns and SOLID priniciples building features
* Don't assume anything when coming to docs, always refer to context7 MCP for docs
* Always cleanup the code by removing unused imports

# Backend
* Use pydantic models every where possible
* Keep files atomic that just does one thing
* Use uv as package manager, use `uv sync`
* Always add unit tests, run unit tests using  `uv run pytest`
* Keep controllers/handlers under api/v0/* light, they should just validate and pass on the logic to service.

# Frontend