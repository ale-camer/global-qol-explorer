"""
Deterministic ETL pipeline that replaces the legacy Google Colab PySpark notebook.
Downloads all 44 indicators from Our World in Data (OWID Grapher), validates and
normalizes types, builds the indexed SQLite snapshot (`backend/data/qol.sqlite`),
optionally syncs to BigQuery, and sends a plain-text WhatsApp notification.
"""

import argparse
import csv
import io
import json
import logging
import math
import os
import sqlite3
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from backend.ingestion.notify_whatsapp import (
    build_whatsapp_message,
    send_whatsapp_notification,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ingest_owid")

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
DEFAULT_SQLITE_PATH = BASE_DIR / "data" / "qol.sqlite"
BASELINE_MANIFEST_PATH = BASE_DIR / "data" / "baseline_backup" / "manifest.json"
OWID_BASE_URL = "https://ourworldindata.org/grapher/{slug}.csv"


def fetch_indicator_csv(
    slug: str,
    indicator_id: int,
    code_to_id: dict[str, int],
    retries: int = 3,
) -> list[tuple[int, int, int, float]]:
    """Download a single OWID CSV and return normalized `(indicator_id, year, country_id, value)` tuples."""
    url = OWID_BASE_URL.format(slug=slug)
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "GlobalQoLExplorer-ETL/2.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw_text = resp.read().decode("utf-8")
            break
        except Exception as exc:
            last_err = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
    else:
        raise RuntimeError(f"Failed to download {slug} after {retries} attempts: {last_err}")

    dedup: dict[tuple[int, int, int], float] = {}
    reader = csv.reader(io.StringIO(raw_text))
    header = next(reader, None)
    if not header or len(header) < 4:
        raise ValueError(f"Unexpected CSV header for {slug}: {header}")

    for row in reader:
        if len(row) < 4:
            continue
        code = row[1].strip()
        country_id = code_to_id.get(code)
        if country_id is None:
            continue
        year_str = row[2].strip()
        val_str = row[3].strip()
        if not year_str or not val_str:
            continue
        try:
            year = int(year_str)
            val = float(val_str)
            if math.isnan(val) or math.isinf(val):
                continue
        except ValueError:
            continue
        dedup[(indicator_id, year, country_id)] = val

    return [(ind_id, yr, cid, val) for (ind_id, yr, cid), val in dedup.items()]


def write_sqlite_snapshot(
    sqlite_path: Path,
    countries: list[dict],
    indicators: list[dict],
    fact_rows: list[tuple[int, int, int, float]],
) -> None:
    """Atomically write the normalized dataset to a compact, clustered SQLite file."""
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = sqlite_path.with_suffix(".sqlite.tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    conn = sqlite3.connect(str(tmp_path))
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA page_size = 4096;")
        cur.execute("PRAGMA journal_mode = OFF;")
        cur.execute("PRAGMA synchronous = OFF;")

        cur.execute(
            """
            CREATE TABLE dim_countries (
                country_id INTEGER PRIMARY KEY,
                country_name TEXT NOT NULL,
                code TEXT NOT NULL UNIQUE,
                continent TEXT
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE dim_indicators (
                indicator_id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                indicator TEXT NOT NULL UNIQUE
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE fact_indicators_compact (
                indicator_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                country_id INTEGER NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (indicator_id, year, country_id)
            ) WITHOUT ROWID;
            """
        )
        cur.execute(
            """
            CREATE VIEW fact_indicators AS
            SELECT
                f.country_id AS country_id,
                f.year AS year,
                d.indicator AS indicator_name,
                f.value AS value
            FROM fact_indicators_compact f
            JOIN dim_indicators d ON f.indicator_id = d.indicator_id;
            """
        )

        cur.executemany(
            "INSERT INTO dim_countries (country_id, country_name, code, continent) VALUES (?, ?, ?, ?);",
            [
                (c["country_id"], c["country_name"], c["code"], c["continent"] or None)
                for c in countries
            ],
        )
        cur.executemany(
            "INSERT INTO dim_indicators (indicator_id, category, indicator) VALUES (?, ?, ?);",
            [(idx, i["category"], i["indicator"]) for idx, i in enumerate(indicators, start=1)],
        )
        cur.executemany(
            "INSERT INTO fact_indicators_compact (indicator_id, year, country_id, value) VALUES (?, ?, ?, ?);",
            fact_rows,
        )
        conn.commit()
        cur.execute("VACUUM;")
    finally:
        conn.close()

    os.replace(tmp_path, sqlite_path)


def run_ingestion(sqlite_path: Path = DEFAULT_SQLITE_PATH, notify: bool = True) -> dict:
    start_ts = time.perf_counter()
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)

    countries = catalog["countries"]
    indicators = catalog["indicators"]
    code_to_id = {c["code"]: c["country_id"] for c in countries}

    baseline_rows = 316500
    if BASELINE_MANIFEST_PATH.exists():
        try:
            with open(BASELINE_MANIFEST_PATH, encoding="utf-8") as mf:
                baseline_rows = json.load(mf).get("fact_indicators", {}).get("rows", 316500)
        except Exception:
            pass

    all_facts: list[tuple[int, int, int, float]] = []
    ok_count = 0
    total_indicators = len(indicators)

    try:
        logger.info("Downloading %d indicators from Our World in Data...", total_indicators)
        with ThreadPoolExecutor(max_workers=8) as pool:
            future_to_slug = {
                pool.submit(
                    fetch_indicator_csv,
                    item["indicator"],
                    idx,
                    code_to_id,
                ): item["indicator"]
                for idx, item in enumerate(indicators, start=1)
            }
            for future in as_completed(future_to_slug):
                slug = future_to_slug[future]
                rows = future.result()
                if not rows:
                    raise RuntimeError(f"Indicator '{slug}' returned 0 rows.")
                all_facts.extend(rows)
                ok_count += 1

        all_facts.sort(key=lambda r: (r[0], r[1], r[2]))
        write_sqlite_snapshot(sqlite_path, countries, indicators, all_facts)

        duration = time.perf_counter() - start_ts
        delta = len(all_facts) - baseline_rows
        msg = build_whatsapp_message(
            success=True,
            indicators_ok=ok_count,
            indicators_total=total_indicators,
            countries_count=len(countries),
            total_rows=len(all_facts),
            delta_rows=delta,
            duration_sec=duration,
        )
        logger.info("Ingestion finished in %.2fs (%d fact rows).", duration, len(all_facts))
        print("\n" + msg + "\n")
        if notify:
            send_whatsapp_notification(msg)

        return {
            "success": True,
            "indicators_ok": ok_count,
            "indicators_total": total_indicators,
            "countries": len(countries),
            "fact_rows": len(all_facts),
            "delta_vs_baseline": delta,
            "duration_sec": round(duration, 2),
        }

    except Exception as exc:
        duration = time.perf_counter() - start_ts
        msg = build_whatsapp_message(
            success=False,
            indicators_ok=ok_count,
            indicators_total=total_indicators,
            countries_count=len(countries),
            total_rows=len(all_facts),
            delta_rows=0,
            duration_sec=duration,
            error_detail=str(exc),
        )
        logger.error("Ingestion failed: %s", exc)
        print("\n" + msg + "\n", file=sys.stderr)
        if notify:
            send_whatsapp_notification(msg)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OWID QoL ingestion pipeline.")
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=DEFAULT_SQLITE_PATH,
        help="Destination path for the SQLite snapshot.",
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="Disable WhatsApp notification dispatch.",
    )
    args = parser.parse_args()
    run_ingestion(sqlite_path=args.sqlite_path, notify=not args.no_notify)


if __name__ == "__main__":
    main()
