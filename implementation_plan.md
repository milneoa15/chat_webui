# Chatbot WebUI Implementation Plan

Build a self-hosted chat experience comparable to Open WebUI that can load GGUF models locally, target AMD GPUs via ROCm-ready llama.cpp runtimes, and expose advanced controls similar to LM Studio. The plan below is structured as executable phases with checklists and verification criteria so progress can be tracked objectively.

## Key Technologies & References
- [FastAPI](https://fastapi.tiangolo.com/) + [uvicorn](https://www.uvicorn.org/) for an async Python backend with streaming endpoints.
- [llama.cpp](https://github.com/ggerganov/llama.cpp) (ROCm build) and [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for GGUF inference; fall back to [llama.cpp server](https://github.com/ggerganov/llama.cpp/tree/master/examples/server) if direct bindings are insufficient.
- [UV package manager](https://docs.astral.sh/uv/) for Python env + dependency management.
- [Vite](https://vitejs.dev/) + React + TypeScript + [Tailwind CSS](https://tailwindcss.com/) for a fast, customizable UI layer.
- [Zustand](https://github.com/pmndrs/zustand) for lightweight client state management.
- [TanStack Query](https://tanstack.com/query/latest) for chat/session data fetching and caching.
- [Playwright](https://playwright.dev/) for end-to-end UI verification.

## MVP Scope Guardrails
- Prioritize a single ROCm llama.cpp runtime and one GGUF model loaded at a time.
- Ship chat streaming, preset knobs, and conversation persistence before touching Docker, desktop shells, or plugins.
- Treat multi-runtime registry, telemetry, and packaging as "Phase 2" concerns to avoid blocking the first usable release.
- Assume a Windows-native workflow (no WSL). Prefer reusing the LM Studio "ROCm llama.cpp (Windows) v1.55.0" runtime pack before attempting new builds.

## Phase 1 - Repository & Tooling Foundation
**Goal:** Establish reproducible environments for backend/frontend and document the developer workflow.

- [ ] Initialize Git repo, add `README.md`, `LICENSE`, and project structure (`backend/`, `frontend/`, `infra/`).
- [ ] Install UV (if missing) and add `uv.lock`, `pyproject.toml`, and scripts (`uv run`, `uv pip compile`).
- [ ] Scaffold FastAPI app with health check endpoint; add `ruff` + `black` configs for lint/format.
- [ ] Create Vite + React + TypeScript project with Tailwind; configure ESLint + Prettier.
- [ ] Define the initial OpenAPI schema (chat stream, model management) and publish a mock server/fixture so frontend work can proceed independently.
- [ ] Add GitHub Actions (or local `invoke` tasks) for lint/test on both stacks.
**Verification:** `uv run pytest` (even if empty), `npm run lint`, and CI workflow succeed; developer docs explain UV usage.

## Phase 2 - ROCm Runtime & Core Backend
**Goal:** Deliver a minimal FastAPI backend that can load one ROCm-enabled GGUF model and stream tokens.

- [ ] Add script to fetch/build llama.cpp with ROCm flags (`LLAMA_HIPBLAS=1`, `LLAMA_CLBLAST=0`) and document prerequisites (ROCm drivers, Visual Studio Build Tools on Windows if compiling locally).
- [ ] Document and automate copying the LM Studio "ROCm llama.cpp (Windows) v1.55.0" runtime pack into the project (hash validation, expected folder layout) as the preferred GGUF engine path.
- [ ] Implement a Python wrapper that loads a single model via `llama_cpp.Llama` (ROCm build) and exposes init/teardown hooks.
- [ ] Provide model lifecycle APIs: upload/select GGUF, load into memory, unload, query VRAM/RAM usage.
- [ ] Define a configuration schema covering context length, GPU layer offload, CPU threads, eval batch size, KV cache placement, `mmap`, and keep-in-memory flags.
- [ ] Add SQLite (SQLModel/SQLAlchemy) persistence for installed models and default config, with Alembic/SQLModel migrations introduced before writing data so later schema changes are safe.
**Verification:** Backend unit tests mock llama.cpp calls; integration test loads TinyLlama GGUF and completes a streamed response locally.

## Phase 3 - Basic Chat UI & Streaming
**Goal:** Ship the first usable chat experience with token streaming and essential settings.

- [ ] Build chat layout: sidebar (model info), conversation pane with streaming tokens, prompt input, and system prompt editor.
- [ ] Implement SSE endpoint (`POST /api/chat/stream`) in FastAPI and consume it via TanStack Query + custom hook.
- [ ] Add minimal settings drawer for context length, GPU offload count, CPU threads, eval batch, KV cache placement, and `mmap`.
- [ ] Provide file/model manager modal for uploading GGUF and showing metadata (quantization, context, parameters).
- [ ] Implement responsive + dark mode styling using Tailwind primitives.
**Verification:** Playwright spec loads mock backend, sends a prompt, and confirms streamed tokens plus settings toggles.

## Phase 4 - Presets, Conversations, and Controls
**Goal:** Match LM Studio-like convenience features while keeping scope constrained.

- [ ] Define preset entities (name, base model, inference parameters) and CRUD API endpoints.
- [ ] Implement conversation schema (title, system prompt, message history, preset snapshot) with trimming warnings.
- [ ] Add message regeneration, stop generation button, token/speed stats, and auto-save drafts.
- [ ] Enable export of conversation as JSON/Markdown and import/export of presets to JSON.
- [ ] Add hotkeys (send `Ctrl+Enter`, toggle settings `Ctrl+,`).
**Verification:** Backend tests cover preset + conversation CRUD; UI e2e validates regeneration, exports, and hotkeys.

## Phase 5 - Runtime Options & Observability
**Goal:** Broaden runtime support (while honoring the LM Studio pack path) and gain better backend insight.

- [ ] Maintain a runtime registry (JSON/YAML) that records the copied LM Studio ROCm pack plus optional CPU/Vulkan engines, including binary paths, capabilities, and validation hashes.
- [ ] Provide commands/UI to register an existing runtime pack (copy, version check) or build a fresh llama.cpp binary locally without WSL; run smoke prompts after each registration.
- [ ] Support launching external runtimes (e.g., llama.cpp server subprocess) and monitoring their health/ports.
- [ ] Add structured logging (`structlog`) with inference timing, token throughput, and GPU resource metrics.
**Verification:** Runtime registry unit tests pass; registering the LM Studio pack succeeds and a health check confirms token generation.

## Phase 6 - Packaging & Delivery
**Goal:** Offer straightforward ways to run or ship the app after runtime options are stable.

- [ ] Package a desktop-friendly distribution (Tauri/Electron) or provide a signed one-click launcher that bundles the preferred runtime pack.
- [ ] Provide Docker/Podman compose setup (UV backend + Node frontend + llama.cpp binaries volume) for users comfortable with containers.
- [ ] Publish scripts that download/copy the LM Studio pack automatically during installation, with checksum enforcement.
**Verification:** Desktop build launches chat end-to-end; Docker compose boots, serves UI, and completes a prompt with the bundled runtime.

## Phase 7 - Monitoring, Telemetry, and Performance
**Goal:** Harden the app for long-running sessions and observability.

- [ ] Emit telemetry endpoints (Prometheus/OpenTelemetry) for inference latency, token throughput, GPU utilization.
- [ ] Benchmark multiple runtimes and store results to power default recommendations.
- [ ] Add health dashboards or CLI summaries for memory pressure and cache hit rates.
**Verification:** Benchmark script outputs reproducible metrics; telemetry endpoints scraped successfully in tests.

## Phase 8 - Documentation & Extension Hooks
**Goal:** Ensure long-term maintainability and allow community extensions.

- [ ] Write operator docs detailing ROCm setup, model download sources (Hugging Face, Ollama), and troubleshooting.
- [ ] Publish API reference (OpenAPI + typed SDK) for custom clients/bots.
- [ ] Expose plugin/event hook system for custom prompt preprocessing or tool execution.
- [ ] Draft roadmap for future integrations (function calling, multimodal, RAG connectors).
**Verification:** Docs lint (`markdownlint`) passes; sample plugin demonstrates hook API.

## Testing & Release Milestones
1. **Milestone A - Local MVP:** Phases 1-3 complete; ROCm model loads (via copied runtime pack), SSE chat works, and essential settings toggle live.
2. **Milestone B - Productivity Suite:** Phase 4 locked; presets, conversations, and regeneration features stable.
3. **Milestone C - Runtime Options:** Phase 5 complete with registry + observability enhancements.
4. **Milestone D - Distribution Ready:** Phase 6 complete with desktop + container delivery paths.
5. **Milestone E - Production Ready:** Phases 7-8; monitoring, docs, and plugin hooks finished.

Each milestone should conclude with: `uv run pytest`, backend integration test against a real GGUF, `npm run test`, Playwright smoke run, and (for Milestone C) full Docker compose validation.

---
This plan keeps UV-focused Python tooling, uses llama.cpp for ROCm GGUF inference, and provides LM Studio-level configurability while building a modern, testable web experience.
