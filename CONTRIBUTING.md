# Contributing to PromptRepo

Thank you for your interest in contributing to PromptRepo! We're excited to have you help make prompt management better for everyone.

## Code of Conduct

Be respectful and constructive. We're all here to build something useful together.

## How to Contribute

### Reporting Bugs

1. Check existing [issues](https://github.com/YOUR_USERNAME/promptrepo/issues) to avoid duplicates
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, browser, versions)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the problem you're solving
3. Explain your proposed solution
4. Consider alternatives you've thought about

### Submitting Code

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptrepo.git
   cd promptrepo
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Set Up Development Environment**

   **Backend:**
   ```bash
   cd backend
   uv sync
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   ```

4. **Make Your Changes**
   - Follow existing code patterns and style
   - Write meaningful commit messages
   - Add tests for new functionality
   - Update documentation if needed

5. **Run Tests**

   **Backend:**
   ```bash
   cd backend
   uv run pytest
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm test
   ```

6. **Submit a Pull Request**
   - Fill out the PR template
   - Link related issues
   - Describe what changed and why

## Development Guidelines

### Backend (Python/FastAPI)

- **Use Pydantic models** everywhere for data validation
- **Keep files atomic** - each file should do one thing well
- **Follow SOLID principles**
- **Dependency Injection**: Use constructor injection pattern; all DI is centralized in `backend/api/deps.py`
- **Controllers**: Keep handlers in `api/v0/*` lightweight - validate and delegate to services
- **Services**: Handle business logic only; inject dependencies via constructor
- **Tests**: Write quality tests that cover all scenarios, not just quantity
- **Imports**: Start from `backend/` directory (e.g., `from services.config import ConfigService`)

**API Endpoint Pattern:**
```python
@router.get(
    "/resource",
    response_model=StandardResponse[ResourceData],
    status_code=status.HTTP_200_OK,
    summary="Get resource",
    description="Detailed description for OpenAPI docs",
    responses={404: {"description": "Resource not found"}}
)
async def get_resource(
    request: Request,
    service: ResourceServiceDep,
) -> StandardResponse[ResourceData]:
    # Raise exceptions (AppException, ValidationException, etc.)
    # Let global handlers deal with them
    return success_response(data)
```

### Frontend (Next.js/React)

- **Zustand for state** - avoid `useEffect` and `React.use` directly
- **TypeScript** - strict types everywhere
- **Proxy pattern** - all API calls go through `/api/[...proxy]/route.ts`
- **Protected routes** - wrap authenticated pages with `ProtectedRoute`
- **Component structure**:
  - `stores/` - Zustand stores (`state.ts`, `actions.ts`, `store.ts`, `hooks.ts`)
  - `services/` - API client functions
  - `components/` - Reusable UI components

### Code Style

**Python:**
- Follow PEP 8
- Use `black` for formatting
- Use `isort` for import sorting

**TypeScript:**
- Follow ESLint rules
- Use consistent naming (camelCase for functions/variables, PascalCase for components)

### Commit Messages

Use clear, descriptive commit messages:
```
feat: add chat sharing functionality
fix: resolve token counting in streaming mode
docs: update API documentation
refactor: simplify prompt service logic
test: add unit tests for evaluations
```

## Project Architecture

```
promptrepo/
├── backend/
│   ├── api/v0/          # API endpoints (auth, llm, prompts, tools, evals, etc.)
│   ├── services/        # Business logic (constructor injection)
│   ├── agents/          # AI agent implementations
│   ├── database/        # SQLModel ORM, DAOs, migrations
│   ├── schemas/         # Pydantic request/response models
│   └── middlewares/     # Exception handling, CORS, context
├── frontend/
│   ├── app/             # Next.js pages (App Router)
│   ├── stores/          # Zustand state management
│   ├── services/        # API client services
│   └── components/      # Reusable UI components
└── docs/                # Architecture documentation
```

## Getting Help

- **Questions?** Open a discussion or issue
- **Stuck?** Describe what you've tried and we'll help

## Recognition

Contributors are recognized in:
- GitHub Contributors list
- Release notes for significant contributions

Thank you for helping make PromptRepo better!
