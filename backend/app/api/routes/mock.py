"""Mock data endpoints powering the frontend before llama.cpp is wired in."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from backend.app.config import settings
from backend.app.schemas.chat import ChatChunk, ChatRequest, ChatResponse
from backend.app.schemas.models import ModelCard

router = APIRouter(prefix="/mock", tags=["mock"])


def _read_fixture(name: str) -> list[dict]:
    fixture_path = settings.fixtures_dir / name
    if not fixture_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fixture '{name}' not found.",
        )

    with Path(fixture_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


@router.get("/models", response_model=list[ModelCard], summary="List mock models")
def list_models() -> list[ModelCard]:
    """Return registered mock models."""
    raw_models = _read_fixture("models.json")
    return [ModelCard(**model) for model in raw_models]


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Return a mock chat stream",
)
def create_mock_chat(request: ChatRequest) -> ChatResponse:
    """Replay a canned stream so the frontend can build against SSE/parsing logic."""
    stream_fixture = _read_fixture("chat_stream.json")
    stream = [ChatChunk(**chunk) for chunk in stream_fixture]
    model_ids = {model.id for model in list_models()}
    if request.model_id not in model_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown model_id '{request.model_id}'.",
        )

    return ChatResponse(model_id=request.model_id, stream=stream)
