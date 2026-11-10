# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import os
import json
from itertools import groupby
from operator import itemgetter

# --- Third-party ---
from fastapi import APIRouter, Depends, HTTPException
from google.cloud import bigquery
from google.cloud.bigquery.client import Client

# --- Project ---
from app.db.session import get_session
from app.core.config import settings
from app.schemas import schemas

# =============================================================================
# CONFIGURATION
# =============================================================================
router = APIRouter()


@router.get("/world-geometry", tags=["Metadata"])
def get_world_geometry():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_root_dir = os.path.join(current_dir, "..", "..", "..")
    file_path = os.path.join(app_root_dir, "api", "static", "world-geometry.json")
    normalized_path = os.path.normpath(file_path)
    with open(normalized_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/countries", response_model=list[schemas.Country], tags=["Metadata"])
def get_countries(client: Client = Depends(get_session)):
    try:
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
        query_job = client.query(query)
        results = [dict(row) for row in query_job]
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators", response_model=list[schemas.IndicatorGroup], tags=["Metadata"])
def get_available_indicators(client: Client = Depends(get_session)):
    try:
        table_id = f"{settings.gcp_project_id}.{settings.bq_dataset}.dim_indicators"
        query = f"""
            SELECT
                category,
                indicator AS indicator_name
            FROM `{table_id}`
            ORDER BY category, indicator_name
        """
        results = [dict(row) for row in client.query(query)]
        return [
            {
                "category": key,
                "indicators": [{"indicator_name": item["indicator_name"]} for item in group],
            }
            for key, group in groupby(results, key=itemgetter("category"))
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/years", response_model=list[int], tags=["Metadata"])
def get_available_years(client: Client = Depends(get_session), indicator: str = ""):
    if not indicator:
        raise HTTPException(status_code=400, detail="Indicator is required")
    try:
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
            return []

        return [int(rows[0].min_year), int(rows[0].max_year)]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
