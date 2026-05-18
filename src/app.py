import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interchange.db"


def search_parts(part_number):
    query = """
    SELECT
        p.part_type AS "Part Type",
        p.oe_part_number AS "OE Part Number",
        p.oem_brand AS "OEM Brand",
        cr.brand AS "Cross Reference Brand",
        cr.part_number AS "Cross Reference Part Number",
        v.year AS "Year",
        v.make AS "Make",
        v.model AS "Model",
        v.engine AS "Engine",
        f.fitment_type AS "Fitment Type"
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
        return pd.read_sql_query(query, conn, params=(search_value, search_value))


st.set_page_config(
    page_title="Automotive Part Interchange Database",
    layout="wide"
)

st.title("Automotive Part Interchange Database")
st.write("Search OE, OEM, and aftermarket part numbers to find compatible vehicle fitment.")

part_number = st.text_input("Enter OE or aftermarket part number")

if st.button("Search"):
    if part_number.strip():
        results = search_parts(part_number)

        if not results.empty:
            st.success(f"Found {len(results)} matching records.")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No matching parts found.")
    else:
        st.error("Please enter a part number.")