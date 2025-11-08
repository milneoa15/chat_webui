"""Application settings and configuration helpers."""

from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    api_prefix: str = "/api"
    project_name: str = "Chatbot WebUI"
    openapi_schema_path: Path = BASE_DIR / "backend" / "openapi" / "schema.yaml"
    fixtures_dir: Path = BASE_DIR / "backend" / "fixtures"

    model_config = {
        "env_prefix": "CHATBOT_",
        "case_sensitive": False,
    }


settings = Settings()
