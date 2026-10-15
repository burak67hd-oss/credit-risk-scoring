"""Shared paths and helpers."""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "default_of_credit_card_clients.csv"
DB_PATH = ROOT / "data" / "credit.db"
SQL_DIR = ROOT / "sql"
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"


def connect() -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def read_named_queries(sql_file: Path) -> dict[str, str]:
    """Split a .sql file into queries, using '-- name: xxx' lines as separators.

    Returns {query_name: sql_text}.
    """
    queries, name, lines = {}, None, []
    for line in sql_file.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("-- name:"):
            if name:
                queries[name] = "\n".join(lines).strip()
            name, lines = line.split(":", 1)[1].strip(), []
        elif name:
            lines.append(line)
    if name:
        queries[name] = "\n".join(lines).strip()
    return queries
