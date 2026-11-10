# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import os

# --- Third-party ---
from google.cloud import bigquery

# --- Project ---
from app.core.config import settings

# =============================================================================
# CONFIGURATION
# =============================================================================
def get_session():
    client = bigquery.Client(project=settings.gcp_project_id)
    try:
        yield client
    finally:
        pass