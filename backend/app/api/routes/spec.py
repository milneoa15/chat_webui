"""Serve the hand-authored OpenAPI schema used by the frontend mock client."""

from fastapi import APIRouter, HTTPException, Response, status

from backend.app.config import settings

router = APIRouter(tags=["spec"])


@router.get(
    "/spec",
    response_class=Response,
    responses={200: {"content": {"application/yaml": {}}}},
    summary="Return mock OpenAPI schema",
)
def get_openapi_spec() -> Response:
    """Serve the YAML file that defines chat + model management endpoints."""
    schema_path = settings.openapi_schema_path
    if not schema_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "OpenAPI schema missing. "
                "Regenerate via `uv run python backend/app/main.py --generate-schema`."
            ),
        )

    payload = schema_path.read_text(encoding="utf-8")
    return Response(content=payload, media_type="application/yaml")
