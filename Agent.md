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
* Always add unit tests, run unit tests using  `uv run pytest`. Don't create a lot of tests but create quality tests that cover all scenarios.
* Keep controllers/handlers under api/v0/* light, they should just validate and pass on the logic to service.
* Don't start imports from `` always consider backend folder is root for python project and start imports from within backend directory.

# Frontend