# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---

# --- Third-party ---
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Project ---

# =============================================================================
# CONFIGURATION
# =============================================================================
class Settings(BaseSettings):
    gcp_project_id: str
    bq_dataset: str
    google_application_credentials: str | None = None
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
