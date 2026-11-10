# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---

# --- Third-party ---
from pydantic_settings import BaseSettings

# --- Project ---

# =============================================================================
# CONFIGURATION
# =============================================================================
class Settings(BaseSettings):
    gcp_project_id: str
    bq_dataset: str
    google_application_credentials: str | None = None
    metadata_cache_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
