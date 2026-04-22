#!/usr/bin/env python3
"""
scripts/ingest.py
-----------------
One-time (or periodic) data ingestion pipeline for The Case Against the Relaunch.

What it does:
  1. Creates data/marvel.db (SQLite) with all project data in one place
  2. Seeds hand-curated CSVs into the database (asm_relaunches, relaunch_multi,
     mcu_films, franchise_boxoffice)
  3. Pulls character metadata via ComicVine API:
     - Issue appearance count, first appearance year (validation)

Usage:
  cd "Business Case for Comics"
  python scripts/ingest.py

Environment variables (set in .env or shell):
  COMICVINE_API_KEY  — register free at comicvine.gamespot.com

The generated data/marvel.db is committed to the repo so the Streamlit app
runs without any API access. Re-run this script to refresh the data at any time.
"""

import os
import re
import sys
import time
import sqlite3
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH  = DATA_DIR / "marvel.db"

# ── Load env (try python-dotenv, fall back to os.environ) ────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass  # dotenv not installed; fall back to shell environment

COMICVINE_KEY = os.getenv("COMICVINE_API_KEY", "")

# ── Characters to pull from ComicVine ────────────────────────────────────────
# Name used in the app → search term for ComicVine name filter
COMICVINE_CHARACTERS = {
    "Spider-Man":               "Spider-Man",
    "Iron Man":                 "Iron Man",
    "Captain America":          "Captain America",
    "Thor":                     "Thor",
    "Hulk":                     "Hulk",
    "Black Panther":            "Black Panther",
    "Doctor Strange":           "Doctor Strange",
    "Star-Lord":                "Star-Lord",
    "Daredevil":                "Daredevil",
    "Hawkeye":                  "Hawkeye",
    "Scarlet Witch":            "Scarlet Witch",
    "Captain Marvel":           "Captain Marvel",
    "Thanos":                   "Thanos",
    "Loki":                     "Loki",
    "Winter Soldier":           "Winter Soldier",
    "Ms. Marvel (Kamala Khan)": "Ms. Marvel",
    "Rocket Raccoon":           "Rocket Raccoon",
    "Shang-Chi":                "Shang-Chi",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# ── ComicVine fetcher ─────────────────────────────────────────────────────────
def fetch_comicvine_character(search_name: str):
    """
    Search ComicVine for a character by name. Returns the best match dict or None.
    Rate-limited to 1 request/second to stay within ComicVine's limits.
    """
    if not COMICVINE_KEY:
        log("  ComicVine key missing — skipping enrichment")
        return None
    try:
        resp = requests.get(
            "https://comicvine.gamespot.com/api/characters/",
            params={
                "api_key":    COMICVINE_KEY,
                "filter":     f"name:{search_name}",
                "format":     "json",
                "field_list": "id,name,real_name,count_of_issue_appearances,"
                              "first_appeared_in_issue,publisher",
                "limit":      5,
            },
            headers={"User-Agent": "CaseAgainstRelaunch/1.0"},
            timeout=15,
        )
        data = resp.json()
        results = data.get("results", [])
        if results:
            # Prefer exact name match
            for r in results:
                if r.get("name", "").lower() == search_name.lower():
                    return r
            return results[0]
        log(f"  ComicVine no results for: {search_name}")
        return None
    except Exception as e:
        log(f"  ComicVine error for {search_name}: {e}")
        return None


def parse_cv_first_year(character_data: dict):
    """Extract first appearance year from ComicVine character record."""
    issue = character_data.get("first_appeared_in_issue")
    if not issue:
        return None
    cover_date = issue.get("cover_date", "")
    if cover_date:
        m = re.match(r"(\d{4})", cover_date)
        return int(m.group(1)) if m else None
    return None


# ── Schema ───────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS mcu_films (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    film_title          TEXT NOT NULL,
    year                INTEGER,
    phase               INTEGER,
    source_quality      TEXT,
    source_run          TEXT,
    source_writer       TEXT,
    rt_score            INTEGER,
    UNIQUE(film_title, year)
);

CREATE TABLE IF NOT EXISTS franchise_boxoffice (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    character           TEXT NOT NULL,
    film_title          TEXT NOT NULL,
    year                INTEGER,
    continuity          TEXT,
    worldwide_gross_m   REAL,
    rt_score            INTEGER,
    note                TEXT,
    UNIQUE(character, film_title, year)
);

CREATE TABLE IF NOT EXISTS asm_relaunches (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    relaunch_volume  INTEGER,
    relaunch_year    INTEGER,
    writer           TEXT,
    issue_num        INTEGER,
    orders           INTEGER,
    data_confidence  TEXT,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS relaunch_multi (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    character        TEXT,
    series_label     TEXT,
    start_year       INTEGER,
    writer           TEXT,
    issue_num        INTEGER,
    orders           INTEGER,
    data_confidence  TEXT
);

CREATE TABLE IF NOT EXISTS comic_characters (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    character                   TEXT NOT NULL UNIQUE,
    comicvine_id                INTEGER,
    real_name                   TEXT,
    count_of_issue_appearances  INTEGER,
    first_appearance_year_api   INTEGER,
    publisher                   TEXT,
    fetched_at                  TEXT
);
"""


# ── Seed from CSVs ─────────────────────────────────────────────────────────
def seed_csvs(conn: sqlite3.Connection):
    log("Seeding hand-curated CSVs...")

    # mcu_films
    path = DATA_DIR / "mcu_films.csv"
    if path.exists():
        df = pd.read_csv(path)
        df.to_sql("mcu_films_csv", conn, if_exists="replace", index=False)
        conn.execute("""
            INSERT OR IGNORE INTO mcu_films
              (film_title, year, phase, source_quality, source_run, source_writer, rt_score)
            SELECT film_title, year, phase, source_quality, source_run, source_writer, rt_score
            FROM mcu_films_csv
        """)
        conn.execute("DROP TABLE IF EXISTS mcu_films_csv")
        log(f"  mcu_films: {len(df)} rows seeded")

    # franchise_boxoffice
    path = DATA_DIR / "franchise_boxoffice.csv"
    if path.exists():
        df = pd.read_csv(path)
        df.to_sql("franchise_boxoffice_csv", conn, if_exists="replace", index=False)
        conn.execute("""
            INSERT OR IGNORE INTO franchise_boxoffice
              (character, film_title, year, continuity, worldwide_gross_m, rt_score, note)
            SELECT character, film_title, year, continuity, worldwide_gross_m, rt_score, note
            FROM franchise_boxoffice_csv
        """)
        conn.execute("DROP TABLE IF EXISTS franchise_boxoffice_csv")
        log(f"  franchise_boxoffice: {len(df)} rows seeded")

    # asm_relaunches
    path = DATA_DIR / "asm_relaunches.csv"
    if path.exists():
        df = pd.read_csv(path)
        df.to_sql("asm_relaunches", conn, if_exists="replace", index=False)
        log(f"  asm_relaunches: {len(df)} rows seeded")

    # relaunch_multi
    path = DATA_DIR / "relaunch_multi.csv"
    if path.exists():
        df = pd.read_csv(path)
        df.to_sql("relaunch_multi", conn, if_exists="replace", index=False)
        log(f"  relaunch_multi: {len(df)} rows seeded")

    conn.commit()


# ── Enrich from ComicVine ────────────────────────────────────────────────────
def enrich_characters_comicvine(conn: sqlite3.Connection):
    if not COMICVINE_KEY:
        log("Skipping ComicVine enrichment (no key)")
        return

    log("Pulling character metadata from ComicVine...")
    now = datetime.now(timezone.utc).isoformat()
    pulled = 0

    for app_name, search_name in COMICVINE_CHARACTERS.items():
        # Skip if already fetched
        existing = conn.execute(
            "SELECT id FROM comic_characters WHERE character = ?", (app_name,)
        ).fetchone()
        if existing:
            log(f"  {app_name}: already in DB, skipping")
            continue

        log(f"  Fetching: {app_name} (searching '{search_name}')...")
        data = fetch_comicvine_character(search_name)
        time.sleep(1.1)   # ComicVine enforces ~1 req/sec

        if not data:
            continue

        cv_id       = data.get("id")
        real_name   = data.get("real_name", {})
        if isinstance(real_name, dict):
            real_name = None
        issue_count = data.get("count_of_issue_appearances")
        first_year  = parse_cv_first_year(data)
        publisher   = data.get("publisher", {})
        if isinstance(publisher, dict):
            publisher = publisher.get("name")

        conn.execute("""
            INSERT OR REPLACE INTO comic_characters
              (character, comicvine_id, real_name, count_of_issue_appearances,
               first_appearance_year_api, publisher, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (app_name, cv_id, real_name, issue_count, first_year, publisher, now))

        pulled += 1
        log(f"    ID: {cv_id} | Issues: {issue_count} | First appearance: {first_year}")

    conn.commit()
    log(f"  ComicVine enrichment complete: {pulled} characters pulled")


# ── Summary ───────────────────────────────────────────────────────────────────
def print_summary(conn: sqlite3.Connection):
    print("\n" + "=" * 55)
    print("  marvel.db summary")
    print("=" * 55)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for (name,) in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"  {name:<35} {count:>5} rows")
    print("=" * 55)
    print(f"  Written to: {DB_PATH}")
    print("=" * 55 + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\nThe Case Against the Relaunch — data ingest pipeline")
    print(f"Target: {DB_PATH}\n")

    if not COMICVINE_KEY:
        print("WARNING: COMICVINE_API_KEY not set. Character enrichment will be skipped.")

    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    conn.commit()

    seed_csvs(conn)
    enrich_characters_comicvine(conn)
    print_summary(conn)
    conn.close()
    log("Done.")


if __name__ == "__main__":
    main()
