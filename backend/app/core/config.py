# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import os

# --- Third-party ---
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Project ---

# =============================================================================
# CONFIGURATION
# =============================================================================
_DEFAULT_SQLITE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "qol.sqlite")
)


class Settings(BaseSettings):
    gcp_project_id: str = "global-qol-explorer"
    bq_dataset: str = "quality_of_life"
    google_application_credentials: str | None = None
    sqlite_snapshot_path: str = _DEFAULT_SQLITE_PATH
    prefer_sqlite_snapshot: bool = True
    metadata_cache_ttl_seconds: int = 3600
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://1.bp.blogspot.com",
        "https://storage.googleapis.com",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
