"""Chat schema definitions shared between API routes and mock fixtures."""

from pydantic import BaseModel, Field


class ChatConfig(BaseModel):
    """Subset of inference parameters exposed in Phase 1 fixtures."""

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.85, ge=0.0, le=1.0)
    max_tokens: int = Field(default=256, gt=0, le=4096)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)


class ChatRequest(BaseModel):
    """Request contract for chat completions."""

    model_id: str = Field(description="Identifier matching a registered GGUF model.")
    prompt: str = Field(min_length=1, description="User prompt to feed the LLM.")
    system_prompt: str = Field(default="You are a helpful assistant.")
    config: ChatConfig = Field(default_factory=ChatConfig)


class ChatChunk(BaseModel):
    """A mock streamed token chunk."""

    token: str
    index: int
    is_final: bool = False


class ChatResponse(BaseModel):
    """Aggregate response returned by the mock chat route."""

    model_id: str
    stream: list[ChatChunk]
