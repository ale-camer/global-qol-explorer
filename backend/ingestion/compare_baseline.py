"""
Compares the newly ingested SQLite snapshot (`backend/data/qol.sqlite`) against
the preserved BigQuery baseline backup (`backend/data/baseline_backup/`).
"""

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BASELINE_DIR = BASE_DIR / "data" / "baseline_backup"
SQLITE_PATH = BASE_DIR / "data" / "qol.sqlite"


def run_comparison(sqlite_path: Path = SQLITE_PATH, baseline_dir: Path = BASELINE_DIR) -> None:
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite snapshot not found at {sqlite_path}")

    # Load baseline
    with open(baseline_dir / "dim_countries.csv", encoding="utf-8") as f:
        base_countries = {int(r["country_id"]): r for r in csv.DictReader(f)}

    with open(baseline_dir / "dim_indicators.csv", encoding="utf-8") as f:
        base_indicators = {r["indicator"]: r["category"] for r in csv.DictReader(f)}

    base_facts: dict[tuple[str, int, int], float] = {}
    base_counts_by_ind: dict[str, int] = defaultdict(int)
    base_years_by_ind: dict[str, set[int]] = defaultdict(set)

    with open(baseline_dir / "fact_indicators.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ind = r["indicator_name"]
            cid = int(r["country_id"])
            yr = int(r["year"])
            val = float(r["value"])
            base_facts[(ind, cid, yr)] = val
            base_counts_by_ind[ind] += 1
            base_years_by_ind[ind].add(yr)

    # Load new SQLite snapshot
    conn = sqlite3.connect(str(sqlite_path))
    try:
        cur = conn.cursor()
        new_countries = {
            row[0]: {"country_name": row[1], "code": row[2], "continent": row[3] or ""}
            for row in cur.execute("SELECT country_id, country_name, code, continent FROM dim_countries")
        }
        new_indicators = {
            row[1]: row[0]
            for row in cur.execute("SELECT category, indicator FROM dim_indicators")
        }

        new_facts: dict[tuple[str, int, int], float] = {}
        new_counts_by_ind: dict[str, int] = defaultdict(int)
        new_years_by_ind: dict[str, set[int]] = defaultdict(set)

        for cid, yr, ind, val in cur.execute("SELECT country_id, year, indicator_name, value FROM fact_indicators"):
            new_facts[(ind, cid, yr)] = float(val)
            new_counts_by_ind[ind] += 1
            new_years_by_ind[ind].add(int(yr))
    finally:
        conn.close()

    print("=" * 72)
    print("PARITY AUDIT: NEW OWID INGESTION vs. BIGQUERY BASELINE BACKUP")
    print("=" * 72)
    print(f"Countries  -> Baseline: {len(base_countries):6,d} | New: {len(new_countries):6,d}")
    print(f"Indicators -> Baseline: {len(base_indicators):6,d} | New: {len(new_indicators):6,d}")
    print(f"Fact Rows  -> Baseline: {len(base_facts):6,d} | New: {len(new_facts):6,d} (Delta: {len(new_facts) - len(base_facts):+,d})")

    overlap_keys = set(base_facts.keys()) & set(new_facts.keys())
    added_keys = set(new_facts.keys()) - set(base_facts.keys())
    removed_keys = set(base_facts.keys()) - set(new_facts.keys())

    exact_val_matches = sum(
        1 for k in overlap_keys if abs(base_facts[k] - new_facts[k]) <= 1e-4 * max(1.0, abs(base_facts[k]))
    )
    revised_by_owid = len(overlap_keys) - exact_val_matches

    print("-" * 72)
    print(f"Overlapping (country, indicator, year) points : {len(overlap_keys):,d}")
    print(f"  - Unchanged values (within 0.01% tol)       : {exact_val_matches:,d}")
    print(f"  - Historical revisions by OWID              : {revised_by_owid:,d}")
    print(f"New data points added by OWID since Nov 2025  : {len(added_keys):,d}")
    print(f"Points retired/restructured by OWID           : {len(removed_keys):,d}")
    print("-" * 72)

    changed_inds = []
    for ind in sorted(base_indicators.keys()):
        b_cnt = base_counts_by_ind[ind]
        n_cnt = new_counts_by_ind[ind]
        b_max_yr = max(base_years_by_ind[ind]) if base_years_by_ind[ind] else 0
        n_max_yr = max(new_years_by_ind[ind]) if new_years_by_ind[ind] else 0
        if b_cnt != n_cnt or b_max_yr != n_max_yr:
            changed_inds.append((ind, b_cnt, n_cnt, b_max_yr, n_max_yr))

    print(f"Indicators with updated row counts or newer years ({len(changed_inds)}/{len(base_indicators)}):")
    for ind, b_cnt, n_cnt, b_yr, n_yr in changed_inds:
        print(f"  • {ind:52s} | rows: {b_cnt:6,d} -> {n_cnt:6,d} ({n_cnt - b_cnt:+5,d}) | max_year: {b_yr} -> {n_yr}")
    print("=" * 72)


if __name__ == "__main__":
    run_comparison()
