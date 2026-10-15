"""Step 1 — Load the raw CSV into a SQLite database and run data-quality checks."""
import csv

from utils import DATA_CSV, DB_PATH, SQL_DIR, connect, read_named_queries


def build_database() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = connect()
    con.executescript((SQL_DIR / "01_schema.sql").read_text(encoding="utf-8"))

    # Read the CSV and insert every row (columns are in the same order as the table)
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        rows = [tuple(float(x) for x in row) for row in reader]

    placeholders = ", ".join(["?"] * len(rows[0]))
    con.executemany(f"INSERT INTO clients VALUES ({placeholders})", rows)
    con.commit()
    print(f"Loaded {len(rows):,} rows into {DB_PATH.name}")

    # Data-quality checks
    print("\nData-quality checks")
    for name, query in read_named_queries(SQL_DIR / "02_data_quality.sql").items():
        result = con.execute(query).fetchall()
        print(f"  {name:<32} {result}")

    # Feature view used by the model
    con.executescript((SQL_DIR / "04_features.sql").read_text(encoding="utf-8"))
    n = con.execute("SELECT COUNT(*) FROM client_features").fetchone()[0]
    print(f"\nView client_features created ({n:,} rows)")
    con.close()


if __name__ == "__main__":
    build_database()
