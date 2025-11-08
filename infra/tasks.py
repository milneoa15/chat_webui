"""Invoke tasks for local automation."""

from pathlib import Path

from invoke import task

ROOT = Path(__file__).resolve().parents[1]


def _frontend(ctx, command: str) -> None:
    ctx.run(f"cd frontend && {command}", echo=True, pty=True)


@task
def lint_backend(ctx) -> None:
    """Run ruff and black in check mode."""
    ctx.run("uv run ruff check backend", echo=True, pty=True)
    ctx.run("uv run black --check backend", echo=True, pty=True)


@task
def test_backend(ctx) -> None:
    """Execute backend pytest suite."""
    ctx.run("uv run pytest", echo=True, pty=True)


@task
def lint_frontend(ctx) -> None:
    """Run the frontend lint command."""
    _frontend(ctx, "npm run lint")


@task(pre=[lint_backend, lint_frontend, test_backend])
def ci(ctx) -> None:  # noqa: ARG001
    """Aggregate task mirroring the Phase 1 CI workflow."""
    print("All checks passed ✅")
