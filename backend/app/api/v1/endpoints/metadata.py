# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import logging
import os
import time
from itertools import groupby
from operator import itemgetter
from typing import Any

# --- Third-party ---
from fastapi import APIRouter, Depends, HTTPException, Response
from google.cloud import bigquery
from google.cloud.bigquery.client import Client

# --- Project ---
from app.db.session import get_session, get_sqlite_conn, has_sqlite_snapshot
from app.core.config import settings
from app.schemas import schemas

# =============================================================================
# CONFIGURATION
# =============================================================================
logger = logging.getLogger(__name__)
router = APIRouter()

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_GEOMETRY_PATH = os.path.normpath(
    os.path.join(_CURRENT_DIR, "..", "..", "..", "api", "static", "world-geometry.json")
)
_WORLD_GEOMETRY_BYTES: bytes | None = None
_METADATA_CACHE: dict[str, tuple[float, Any]] = {}


def _get_cached(key: str) -> Any | None:
    entry = _METADATA_CACHE.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if time.monotonic() >= expires_at:
        _METADATA_CACHE.pop(key, None)
        return None
    return value


def _set_cached(key: str, value: Any) -> Any:
    ttl = max(0, settings.metadata_cache_ttl_seconds)
    if ttl > 0:
        _METADATA_CACHE[key] = (time.monotonic() + ttl, value)
    return value


@router.get("/world-geometry", tags=["Metadata"])
def get_world_geometry():
    global _WORLD_GEOMETRY_BYTES
    try:
        if _WORLD_GEOMETRY_BYTES is None:
            with open(_GEOMETRY_PATH, "rb") as f:
                _WORLD_GEOMETRY_BYTES = f.read()
        return Response(
            content=_WORLD_GEOMETRY_BYTES,
            media_type="application/json",
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except Exception:
        logger.exception("Failed to read world-geometry.json")
        raise HTTPException(status_code=500, detail="Internal error loading world geometry.")


@router.get("/countries", response_model=list[schemas.Country], tags=["Metadata"])
def get_countries(client: Client | None = Depends(get_session)):
    cached = _get_cached("countries")
    if cached is not None:
        return cached
    try:
        if has_sqlite_snapshot():
            with get_sqlite_conn() as conn:
                rows = conn.execute(
                    "SELECT country_id, country_name, code, continent FROM dim_countries ORDER BY country_name"
                ).fetchall()
                results = [dict(r) for r in rows]
        else:
            table_id = f"{settings.gcp_project_id}.{settings.bq_dataset}.dim_countries"
            query = f"""
                SELECT 
                    country_id, 
                    country_name, 
                    code, 
                    continent 
                FROM `{table_id}` 
                ORDER BY country_name
            """
            results = [dict(row) for row in client.query(query)]
        return _set_cached("countries", results)
    except Exception:
        logger.exception("Failed to query countries metadata")
        raise HTTPException(status_code=500, detail="Internal error retrieving countries.")


@router.get("/indicators", response_model=list[schemas.IndicatorGroup], tags=["Metadata"])
def get_available_indicators(client: Client | None = Depends(get_session)):
    cached = _get_cached("indicators")
    if cached is not None:
        return cached
    try:
        if has_sqlite_snapshot():
            with get_sqlite_conn() as conn:
                rows = conn.execute(
                    "SELECT category, indicator AS indicator_name FROM dim_indicators ORDER BY category, indicator_name"
                ).fetchall()
                results = [dict(r) for r in rows]
        else:
            table_id = f"{settings.gcp_project_id}.{settings.bq_dataset}.dim_indicators"
            query = f"""
                SELECT
                    category,
                    indicator AS indicator_name
                FROM `{table_id}`
                ORDER BY category, indicator_name
            """
            results = [dict(row) for row in client.query(query)]
        grouped = [
            {
                "category": key,
                "indicators": [{"indicator_name": item["indicator_name"]} for item in group],
            }
            for key, group in groupby(results, key=itemgetter("category"))
        ]
        return _set_cached("indicators", grouped)
    except Exception:
        logger.exception("Failed to query indicators metadata")
        raise HTTPException(status_code=500, detail="Internal error retrieving indicators.")


@router.get("/years", response_model=list[int], tags=["Metadata"])
def get_available_years(client: Client | None = Depends(get_session), indicator: str = ""):
    if not indicator:
        raise HTTPException(status_code=400, detail="Indicator is required")
    cache_key = f"years:{indicator}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    try:
        if has_sqlite_snapshot():
            with get_sqlite_conn() as conn:
                row = conn.execute(
                    """
                    SELECT MIN(f.year) AS min_year, MAX(f.year) AS max_year
                    FROM fact_indicators_compact f
                    JOIN dim_indicators d ON f.indicator_id = d.indicator_id
                    WHERE d.indicator = ?
                    """,
                    (indicator,),
                ).fetchone()
                if not row or row["min_year"] is None or row["max_year"] is None:
                    return _set_cached(cache_key, [])
                return _set_cached(cache_key, [int(row["min_year"]), int(row["max_year"])])

        table_id = f"{settings.gcp_project_id}.{settings.bq_dataset}.fact_indicators"
        query = f"""
            SELECT
                MIN(SAFE_CAST(year AS INT64)) AS min_year,
                MAX(SAFE_CAST(year AS INT64)) AS max_year
            FROM `{table_id}`
            WHERE indicator_name = @indicator
              AND SAFE_CAST(year AS INT64) IS NOT NULL
              AND SAFE_CAST(value AS FLOAT64) IS NOT NULL
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("indicator", "STRING", indicator),
            ]
        )
        rows = list(client.query(query, job_config=job_config).result())
        if not rows or rows[0].min_year is None or rows[0].max_year is None:
            return _set_cached(cache_key, [])

        bounds = [int(rows[0].min_year), int(rows[0].max_year)]
        return _set_cached(cache_key, bounds)
    except Exception:
        logger.exception("Failed to query available years for indicator=%s", indicator)
        raise HTTPException(status_code=500, detail="Internal error retrieving available years.")
