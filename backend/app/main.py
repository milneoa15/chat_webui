"""FastAPI application factory."""

from fastapi import FastAPI

from backend.app.api.routes import health, mock, runtime, spec
from backend.app.config import settings
from backend.app.db.session import init_db
from backend.app.version import __version__


def create_app() -> FastAPI:
    """Instantiate the FastAPI application."""
    init_db()
    app = FastAPI(title=settings.project_name, version=__version__)
    for router in (health.router, mock.router, runtime.router, spec.router):
        app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()


def main() -> None:
    """Entrypoint used by `uv run backend` scripts."""
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
