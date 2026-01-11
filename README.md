# PromptRepo

**Take back control of your System Prompts. Store them in your repository, not in scattered services.**

[![Beta](https://img.shields.io/badge/status-beta-yellow)](https://promptrepo.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/demo-promptrepo.dev-green)](https://promptrepo.dev)

> **Note:** This project is currently in **beta**. We welcome feedback and contributions!

## The Problem

Managing AI system prompts across environments is painful:
- Prompts scattered across different LLM provider dashboards
- No version control or change history
- Difficult collaboration between developers and product owners
- Infrastructure overhead for each environment
- No easy way to test prompt changes before deployment

## The Solution

PromptRepo brings your system prompts into your Git repository where they belong. Treat prompts like code - version them, review them, and deploy them with confidence.

**Try it live at [promptrepo.dev](https://promptrepo.dev)**

## Key Features

### Chat Playground
Interactive testing environment where anyone - developers, product owners, QA - can chat with your AI agent using the system prompt. See exactly how your agent behaves in real scenarios without writing code.

### Prompt Optimizer
AI-powered prompt enhancement that follows provider-specific best practices:
- **OpenAI**: GPT-4.1+ optimizations, precision patterns
- **Anthropic**: XML tags, step-by-step thinking
- **Google Gemini**: Direct, efficient prompting
- **OWASP 2025 Guardrails**: Optional prompt injection protection

### Tool Mocking
Define tools/functions and mock their responses to test how your agent handles different scenarios. Perfect for testing edge cases without calling real APIs.

### Evaluations
Run unit tests, semantic similarity checks, and complex evaluations against your prompts:
- Built-in metrics (correctness, hallucination, bias detection)
- Custom evaluation definitions
- Batch execution with history tracking

### Share Conversations
Generate shareable links for chat sessions. Show colleagues exactly how your agent performs in specific scenarios - great for demos, reviews, and debugging.

### Git-Native Workflow
Every change you make automatically updates your Git branch. Create a PR, iterate on your prompts, and merge when ready. You never lose your work and never worry about syncing - it's just Git.

### Multi-Provider Support
Connect your own API keys and switch between providers:
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude family)
- Google (Gemini models)
- Mistral
- And more...

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **uv** - Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Git**

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptrepo.git
   cd promptrepo
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the backend**
   ```bash
   cd backend
   uv sync
   uv run uvicorn main:app --reload --port 8080
   ```

4. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Docker Development

```bash
docker-compose -f docker-compose.dev.yml up
```

## Project Structure

```
promptrepo/
├── backend/                 # Python FastAPI backend
│   ├── api/v0/             # Versioned API endpoints
│   ├── services/           # Business logic layer
│   ├── agents/             # AI agent implementations
│   ├── database/           # SQLModel ORM & migrations
│   └── tests/              # Unit & integration tests
├── frontend/               # Next.js React application
│   ├── app/                # Pages (App Router)
│   ├── stores/             # Zustand state management
│   ├── services/           # API client services
│   └── components/         # Reusable UI components
├── docs/                   # Architecture documentation
└── persistence/            # Shared storage for Git repos
```

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLModel** - ORM combining SQLAlchemy + Pydantic
- **GitPython** - Git repository operations
- **DeepEval** - LLM evaluation framework
- **any-llm** / **any-agent** - Multi-provider LLM abstractions

### Frontend
- **Next.js 15** - React framework with SSR
- **React 19** - UI library
- **Zustand** - Lightweight state management
- **Chakra UI** - Component library
- **TypeScript** - Type safety

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection string |
| `GITHUB_CLIENT_ID` | GitHub OAuth app client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app secret |
| `HOSTING_TYPE` | `INDIVIDUAL` or `ORGANIZATION` |
| `REPO_PATH` | Path to prompt repository storage |

See [.env.example](.env.example) for all available options.

## Running Tests

### Backend
```bash
cd backend
uv run pytest
```

### Frontend
```bash
cd frontend
npm test
```

## Roadmap

We're actively working on:

- [ ] **Auto-migration tooling** - Generate YAML metadata from existing repos for quick PromptRepo adoption
- [ ] **CI/CD integration** - Run prompt evaluations in your pipeline
- [ ] **Prompt versioning UI** - Visual diff and history
- [ ] **More evaluation metrics** - Custom metric definitions
- [ ] **Prompt templates** - Reusable prompt patterns

## Contributing

We love contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Before submitting a PR:
1. Ensure tests pass (`uv run pytest` for backend, `npm test` for frontend)
2. Follow existing code patterns
3. Update documentation if needed

## Feedback

This is a beta release - your feedback shapes the future of PromptRepo!

- **Try it out**: [promptrepo.dev](https://promptrepo.dev)
- **Report issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/promptrepo/issues)
- **Share feedback**: We'd love to hear how you're using PromptRepo

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Stop managing prompts in scattered dashboards. Start managing them like code.**
