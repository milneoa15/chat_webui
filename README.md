# Chatbot WebUI

Self-hosted chat experience targeting local GGUF models accelerated via ROCm-ready `llama.cpp`. The project is split across a FastAPI backend (Python/UV) and a Vite + React TypeScript frontend for rapid iteration.

## Repository layout

- `backend/` – FastAPI app, OpenAPI schema, mock fixtures, and Python tooling.
- `frontend/` – Vite + React + Tailwind UI with TanStack Query + Zustand state.
- `infra/` – CI workflows, Invoke tasks, and future deployment scripts.

## Getting started

1. **Python toolchain**
   ```bash
   uv sync
   uv run fastapi dev backend/app/main.py
   ```
   The backend exposes a health endpoint at `/api/health` and serves mock chat/model schemas for the frontend.

2. **Frontend toolchain**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The UI consumes the mock OpenAPI fixtures by default so it can be built before llama.cpp is wired in.

3. **Quality gates**
   ```bash
   uv run ruff check
   uv run ruff format --check
   uv run pytest
   cd frontend && npm run lint
   ```

See `implementation_plan.md` for the full multi-phase roadmap. Phase 1 focuses on reproducible environments and developer tooling; later phases add ROCm runtimes, chat streaming, and packaging.
