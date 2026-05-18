import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interchange.db"


def run_query():
    query = """
    SELECT
        p.part_type,
        p.oe_part_number,
        p.oem_brand,
        v.year,
        v.make,
        v.model,
        v.engine,
        f.fitment_type
    FROM fitment f
    JOIN parts p ON f.part_id = p.part_id
    JOIN vehicles v ON f.vehicle_id = v.vehicle_id;
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

    for row in rows:
        print(row)


if __name__ == "__main__":
    run_query()