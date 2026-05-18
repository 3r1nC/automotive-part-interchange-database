import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interchange.db"


def search_by_part_number(part_number):
    query = """
    SELECT
        p.part_type,
        p.oe_part_number,
        p.oem_brand,
        cr.brand AS interchange_brand,
        cr.part_number AS interchange_part_number,
        v.year,
        v.make,
        v.model,
        v.engine,
        f.fitment_type
    FROM parts p
    LEFT JOIN cross_references cr ON p.part_id = cr.part_id
    LEFT JOIN fitment f ON p.part_id = f.part_id
    LEFT JOIN vehicles v ON f.vehicle_id = v.vehicle_id
    WHERE
        p.oe_part_number LIKE ?
        OR cr.part_number LIKE ?;
    """

    search_value = f"%{part_number}%"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (search_value, search_value))
        rows = cursor.fetchall()

    return rows


if __name__ == "__main__":
    user_input = input("Enter OE or aftermarket part number: ")
    results = search_by_part_number(user_input)

    if results:
        for row in results:
            print(row)
    else:
        print("No matching parts found.")