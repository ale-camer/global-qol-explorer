# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import os
import sqlite3

# --- Third-party ---
from google.cloud import bigquery

# --- Project ---
from app.core.config import settings

# =============================================================================
# CONFIGURATION
# =============================================================================
_bq_client: bigquery.Client | None = None


def has_sqlite_snapshot() -> bool:
    return bool(
        settings.prefer_sqlite_snapshot
        and settings.sqlite_snapshot_path
        and os.path.isfile(settings.sqlite_snapshot_path)
    )


def get_sqlite_conn() -> sqlite3.Connection:
    uri = f"file:{settings.sqlite_snapshot_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_bq_client() -> bigquery.Client | None:
    global _bq_client
    if has_sqlite_snapshot():
        return None
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


def get_session() -> bigquery.Client | None:
    if has_sqlite_snapshot():
        yield None
    else:
        yield init_bq_client()
