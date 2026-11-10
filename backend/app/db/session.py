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
_bq_client: bigquery.Client | None = None


def init_bq_client() -> bigquery.Client:
    global _bq_client
    if _bq_client is None:
        if settings.google_application_credentials and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
        _bq_client = bigquery.Client(project=settings.gcp_project_id)
    return _bq_client


def close_bq_client() -> None:
    global _bq_client
    if _bq_client is not None:
        _bq_client.close()
        _bq_client = None


def get_session():
    yield init_bq_client()
