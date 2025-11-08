"""Model metadata schema."""

from pydantic import BaseModel, Field


class ModelCard(BaseModel):
    """Metadata about an available GGUF artifact."""

    id: str = Field(description="Unique identifier for the model in the runtime registry.")
    name: str = Field(description="Human friendly display name.")
    quantization: str = Field(description="GGUF quantization preset, e.g. Q4_K_M.")
    context_length: int = Field(description="Maximum context tokens supported by the model.")
    parameter_count: float = Field(description="Parameter count in billions.")
    description: str = Field(default="")
