# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import os

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
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()