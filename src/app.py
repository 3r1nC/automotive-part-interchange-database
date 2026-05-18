import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interchange.db"


def get_filter_options(column_name, table_name):
    query = f"""
    SELECT DISTINCT {column_name}
    FROM {table_name}
    WHERE {column_name} IS NOT NULL
    ORDER BY {column_name};
    """

    with sqlite3.connect(DB_PATH) as conn:
        results = pd.read_sql_query(query, conn)

    return results[column_name].tolist()


def search_parts(part_number="", year=None, make=None, model=None):
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
    WHERE 1=1
    """

    params = []

    if part_number:
        query += """
        AND (
            p.oe_part_number LIKE ?
            OR cr.part_number LIKE ?
        )
        """
        search_value = f"%{part_number}%"
        params.extend([search_value, search_value])

    if year:
        query += " AND v.year = ?"
        params.append(year)

    if make:
        query += " AND v.make = ?"
        params.append(make)

    if model:
        query += " AND v.model = ?"
        params.append(model)

    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


st.set_page_config(
    page_title="Automotive Part Interchange Database",
    layout="wide"
)

st.title("Automotive Part Interchange Database")

st.write(
    "Search OE, OEM, and aftermarket part numbers "
    "and filter by vehicle information."
)

# FILTERS

years = get_filter_options("year", "vehicles")
makes = get_filter_options("make", "vehicles")
models = get_filter_options("model", "vehicles")

col1, col2, col3 = st.columns(3)

with col1:
    selected_year = st.selectbox(
        "Year",
        options=[""] + years
    )

with col2:
    selected_make = st.selectbox(
        "Make",
        options=[""] + makes
    )

with col3:
    selected_model = st.selectbox(
        "Model",
        options=[""] + models
    )

part_number = st.text_input(
    "Enter OE or aftermarket part number"
)

if st.button("Search"):

    results = search_parts(
        part_number=part_number,
        year=selected_year if selected_year != "" else None,
        make=selected_make if selected_make != "" else None,
        model=selected_model if selected_model != "" else None
    )

    if not results.empty:
        st.success(f"Found {len(results)} matching records.")
        st.dataframe(results, use_container_width=True)
    else:
        st.warning("No matching records found.")