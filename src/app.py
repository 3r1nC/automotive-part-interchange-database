import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from import_data import main as initialize_database

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interchange.db"

if not DB_PATH.exists():
    initialize_database()


def get_years():
    query = """
    SELECT DISTINCT year
    FROM vehicles
    ORDER BY year;
    """

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn)

    return df["year"].tolist()


def get_makes(year=None):
    query = """
    SELECT DISTINCT make
    FROM vehicles
    WHERE 1=1
    """

    params = []

    if year:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY make;"

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    return df["make"].tolist()


def get_models(year=None, make=None):
    query = """
    SELECT DISTINCT model
    FROM vehicles
    WHERE 1=1
    """

    params = []

    if year:
        query += " AND year = ?"
        params.append(year)

    if make:
        query += " AND make = ?"
        params.append(make)

    query += " ORDER BY model;"

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    return df["model"].tolist()


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

    query += """
    ORDER BY
        v.year DESC,
        v.make,
        v.model,
        p.part_type;
    """

    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


st.set_page_config(
    page_title="Lyzatech Automotive Interchange Platform",
    layout="wide"
)

st.sidebar.title("Lyzatech")
st.sidebar.caption("Automotive Parts Intelligence Platform")
st.sidebar.image("assets/lyzatech-logo.png", width=150)

st.title("Lyzatech Automotive Interchange Platform")

st.write(
    "Search OE, OEM, and aftermarket part numbers, or filter by vehicle "
    "to identify compatible automotive parts."
)

st.divider()

st.subheader("Vehicle Filters")

years = get_years()

col1, col2, col3 = st.columns(3)

with col1:
    selected_year = st.selectbox(
        "Year",
        options=[""] + years
    )

makes = get_makes(
    year=selected_year if selected_year != "" else None
)

with col2:
    selected_make = st.selectbox(
        "Make",
        options=[""] + makes
    )

models = get_models(
    year=selected_year if selected_year != "" else None,
    make=selected_make if selected_make != "" else None
)

with col3:
    selected_model = st.selectbox(
        "Model",
        options=[""] + models
    )

st.subheader("Part Number Search")

part_number = st.text_input(
    "Enter OE or aftermarket part number",
    placeholder="Example: FL-500S or PH10575"
)

search_clicked = st.button("Search")

if search_clicked:
    results = search_parts(
        part_number=part_number.strip(),
        year=selected_year if selected_year != "" else None,
        make=selected_make if selected_make != "" else None,
        model=selected_model if selected_model != "" else None
    )

    if not results.empty:
        st.success(f"Found {len(results)} matching records.")
        st.dataframe(results, use_container_width=True)
    else:
        st.warning("No matching records found.")

st.divider()

st.caption(
    "Built by Lyzatech • Prototype Interchange Intelligence Platform"
)