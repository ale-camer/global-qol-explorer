# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---

# --- Third-party ---
from fastapi import APIRouter

# --- Project ---
from app.api.v1.endpoints import metadata, data

# =============================================================================
# CONFIGURATION
# =============================================================================
api_router = APIRouter()
api_router.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])
api_router.include_router(data.router, prefix="/data", tags=["Data Queries"])
