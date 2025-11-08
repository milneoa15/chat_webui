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

    data_dir: Path = BASE_DIR / ".state"
    models_dir: Path = data_dir / "models"
    runtime_root: Path = BASE_DIR / "runtime"
    preferred_runtime_path: Path = runtime_root / "lmstudio-rocm-1.55.0"

    database_path: Path = data_dir / "chatbot.db"
    database_url: str = f"sqlite:///{(BASE_DIR / '.state' / 'chatbot.db').as_posix()}"

    model_config = {
        "env_prefix": "CHATBOT_",
        "case_sensitive": False,
    }

    def ensure_directories(self) -> None:
        """Create directories that must exist before the app starts."""
        for path in (self.data_dir, self.models_dir, self.runtime_root):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
