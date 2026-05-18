import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "interchange.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"


def create_database():
    DATABASE_DIR.mkdir(exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())

    print("Database created successfully.")


def import_csv(table_name, csv_file):
    csv_path = DATA_DIR / csv_file

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}")

    df = pd.read_csv(csv_path)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(table_name, conn, if_exists="append", index=False)

    print(f"Imported {csv_file} into {table_name}.")


def main():
    create_database()

    import_csv("vehicles", "sample_vehicles.csv")
    import_csv("parts", "sample_parts.csv")
    import_csv("cross_references", "sample_cross_reference.csv")
    import_csv("fitment", "sample_fitment.csv")

    print("All sample data imported successfully.")


if __name__ == "__main__":
    main()