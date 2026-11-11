# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---
import logging
from typing import Literal

# --- Third-party ---
from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.get("", response_model=list[schemas.Data], tags=["Data Queries"])
@router.get("/", response_model=list[schemas.Data], tags=["Data Queries"], include_in_schema=False)
def get_indicator_data(
    indicator_name: str = Query(..., min_length=1, max_length=200, description="Indicator name"),
    start_year: int = Query(..., ge=1000, le=2100, description="Beginning year for range."),
    end_year: int = Query(..., ge=1000, le=2100, description="Ending year for range."),
    sort_by: Literal[
        "country_asc", "country_desc", "value_asc", "value_desc"
    ] = Query("country_asc", description="Sorting order"),
    client: Client | None = Depends(get_session)
):
    if start_year > end_year:
        raise HTTPException(
            status_code=422,
            detail="start_year must be less than or equal to end_year.",
        )

    sort_options = {
        "country_asc": "name ASC",
        "country_desc": "name DESC",
        "value_asc": "value ASC",
        "value_desc": "value DESC",
    }
    order_by_clause = sort_options.get(sort_by, "name ASC")

    try:
        if has_sqlite_snapshot():
            sql = f"""
                SELECT
                    c.code AS iso_a3,
                    c.country_name AS name,
                    AVG(f.value) AS value
                FROM fact_indicators_compact f
                JOIN dim_indicators d ON f.indicator_id = d.indicator_id
                JOIN dim_countries c ON f.country_id = c.country_id
                WHERE d.indicator = ?
                  AND f.year BETWEEN ? AND ?
                GROUP BY c.code, c.country_name
                ORDER BY {order_by_clause}
            """
            with get_sqlite_conn() as conn:
                rows = conn.execute(sql, (indicator_name, start_year, end_year)).fetchall()
                results = [dict(r) for r in rows]
            logger.info(
                "SQLite query executed for indicator=%s (%d-%d), rows=%d",
                indicator_name,
                start_year,
                end_year,
                len(results),
            )
            return results

        fact_table = f"{settings.gcp_project_id}.{settings.bq_dataset}.fact_indicators"
        countries_table = f"{settings.gcp_project_id}.{settings.bq_dataset}.dim_countries"

        query_str = f"""
            WITH FilteredFacts AS (
                SELECT
                    country_id,
                    SAFE_CAST(value AS FLOAT64) as numeric_value
                FROM `{fact_table}`
                WHERE indicator_name = @indicator_name
                  AND SAFE_CAST(year AS INT64) BETWEEN @start_year AND @end_year
                  AND SAFE_CAST(value AS FLOAT64) IS NOT NULL
            )
            SELECT
                c.code AS iso_a3,
                c.country_name AS name,
                AVG(ff.numeric_value) AS value
            FROM FilteredFacts ff
            JOIN `{countries_table}` c ON ff.country_id = c.country_id
            GROUP BY c.code, c.country_name
            ORDER BY {order_by_clause};
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("indicator_name", "STRING", indicator_name),
                bigquery.ScalarQueryParameter("start_year", "INT64", start_year),
                bigquery.ScalarQueryParameter("end_year", "INT64", end_year),
            ]
        )

        query_job = client.query(query_str, job_config=job_config)
        results = [dict(row) for row in query_job]
        logger.info(
            "BigQuery executed for indicator=%s (%d-%d), rows=%d",
            indicator_name,
            start_year,
            end_year,
            len(results),
        )
        return results

    except Exception:
        logger.exception(
            "Query execution failed for indicator=%s (%d-%d)",
            indicator_name,
            start_year,
            end_year,
        )
        raise HTTPException(status_code=500, detail="Error interno al ejecutar la query.")
