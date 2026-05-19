import base64
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from import_data import main as initialize_database

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interchange.db"

ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "lyzatech-logo.png"
HERO_BG_PATH = ASSETS_DIR / "hero-bg-reference.png"

if not DB_PATH.exists():
    initialize_database()

st.set_page_config(
    page_title="Lyzatech Automotive Interchange Platform",
    page_icon="🔧",
    layout="wide",
)


def image_to_base64(path):
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


hero_bg = image_to_base64(HERO_BG_PATH)

st.html(f"""
<style>
.block-container {{
    padding-top: 1.5rem;
    max-width: 1280px;
}}

[data-testid="stSidebar"] {{
    background: #f8fafc;
    border-right: 1px solid #e5e7eb;
}}

.hero {{
    background:
        linear-gradient(90deg, rgba(2,6,23,.97) 0%, rgba(15,23,42,.9) 42%, rgba(30,64,175,.35) 100%),
        url("data:image/png;base64,{hero_bg}");
    background-size: cover;
    background-position: center right;
    border-radius: 18px;
    padding: 2.75rem;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 16px 40px rgba(15, 23, 42, .2);
}}

.hero h1 {{
    font-size: 2.75rem;
    line-height: 1.1;
    font-weight: 800;
    margin-bottom: 1rem;
}}

.hero p {{
    font-size: 1.05rem;
    color: #dbeafe;
    max-width: 620px;
}}

.metric-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .9rem;
    margin-top: 1.75rem;
    max-width: 1000px;
}}

.metric-card {{
    background: rgba(15,23,42,.78);
    border: 1px solid rgba(147,197,253,.35);
    border-radius: 14px;
    padding: 1rem;
    display: flex;
    gap: .85rem;
    align-items: center;
}}

.metric-icon {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: rgba(37,99,235,.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
}}

.metric-value {{
    font-size: 1.65rem;
    font-weight: 800;
}}

.metric-label {{
    color: #bfdbfe;
    font-size: .85rem;
}}

.footer {{
    text-align: center;
    color: #64748b;
    font-size: .85rem;
    margin-top: 2rem;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 18px !important;
    box-shadow: 0 10px 26px rgba(15, 23, 42, .06);
}}

div.stButton > button {{
    background: #0b1220;
    color: white;
    border-radius: 10px;
    font-weight: 700;
    border: none;
    padding: .6rem 1.35rem;
}}

div.stButton > button:hover {{
    background: #1e40af;
    color: white;
}}

div.stDownloadButton > button {{
    border-radius: 10px;
    font-weight: 700;
}}

[data-testid="stDataFrame"] {{
    overflow-x: auto;
}}

@media (max-width: 768px) {{
    .block-container {{
        padding: 1rem;
        max-width: 100%;
    }}

    .hero {{
        padding: 1.5rem;
        border-radius: 16px;
        background-position: center;
    }}

    .hero h1 {{
        font-size: 2rem;
        line-height: 1.15;
    }}

    .hero p {{
        font-size: .95rem;
    }}

    .metric-row {{
        grid-template-columns: 1fr;
        gap: .75rem;
    }}

    .metric-card {{
        padding: .85rem;
    }}

    .metric-value {{
        font-size: 1.4rem;
    }}

    .metric-label {{
        font-size: .8rem;
    }}

    div.stButton > button {{
        width: 100%;
        margin-bottom: .5rem;
    }}

    div.stDownloadButton > button {{
        width: 100%;
    }}
}}
</style>
""")


def run_scalar_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn).iloc[0, 0]


def get_years():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            "SELECT DISTINCT year FROM vehicles ORDER BY year;",
            conn,
        )
    return df["year"].tolist()


def get_makes(year=None):
    query = "SELECT DISTINCT make FROM vehicles WHERE 1=1"
    params = []

    if year:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY make;"

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    return df["make"].tolist()


def get_models(year=None, make=None):
    query = "SELECT DISTINCT model FROM vehicles WHERE 1=1"
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

    query += " ORDER BY v.year DESC, v.make, v.model, p.part_type, cr.brand;"

    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


def reset_filters():
    st.session_state["selected_year"] = "All Years"
    st.session_state["selected_make"] = "All Makes"
    st.session_state["selected_model"] = "All Models"
    st.session_state["part_number"] = ""


part_count = run_scalar_query("SELECT COUNT(*) FROM parts;")
vehicle_count = run_scalar_query("SELECT COUNT(*) FROM vehicles;")
fitment_count = run_scalar_query("SELECT COUNT(*) FROM fitment;")
cross_ref_count = run_scalar_query("SELECT COUNT(*) FROM cross_references;")


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width="stretch")

    st.markdown("## Lyzatech")
    st.caption("Automotive Parts Intelligence Platform")

    st.divider()

    st.markdown("### Platform Features")
    st.write("🔎 OE/OEM Lookup")
    st.write("🔁 Aftermarket Cross-Reference")
    st.write("🚘 Vehicle Fitment Filtering")
    st.write("🗄️ SQLite Database Backend")

    st.divider()

    st.info(
        "Prototype platform built by Lyzatech to demonstrate an automotive "
        "parts interchange database."
    )

    st.caption("Prototype v1.0")
    st.caption("© 2026 Lyzatech")


st.html(f"""
<div class="hero">
    <h1>Lyzatech Automotive<br>Interchange Platform</h1>
    <p>
        A professional prototype for searching OE, OEM, and aftermarket part
        numbers across compatible vehicle fitment records.
    </p>

    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-icon">⬢</div>
            <div>
                <div class="metric-value">{part_count:,}</div>
                <div class="metric-label">Parts in Database</div>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-icon">🚘</div>
            <div>
                <div class="metric-value">{vehicle_count:,}</div>
                <div class="metric-label">Vehicles Indexed</div>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-icon">🔗</div>
            <div>
                <div class="metric-value">{fitment_count:,}</div>
                <div class="metric-label">Vehicle Fitments</div>
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-icon">🗄️</div>
            <div>
                <div class="metric-value">{cross_ref_count:,}</div>
                <div class="metric-label">Cross References</div>
            </div>
        </div>
    </div>
</div>
""")


with st.container(border=True):
    st.subheader("🔎 Search Vehicle Fitment")

    years = get_years()

    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    with col1:
        selected_year = st.selectbox(
            "Year",
            options=["All Years"] + years,
            key="selected_year",
        )

    makes = get_makes(
        year=selected_year if selected_year != "All Years" else None
    )

    with col2:
        selected_make = st.selectbox(
            "Make",
            options=["All Makes"] + makes,
            key="selected_make",
        )

    models = get_models(
        year=selected_year if selected_year != "All Years" else None,
        make=selected_make if selected_make != "All Makes" else None,
    )

    with col3:
        selected_model = st.selectbox(
            "Model",
            options=["All Models"] + models,
            key="selected_model",
        )

    part_number = st.text_input(
        "Part Number",
        placeholder="Search by OE or aftermarket number, e.g. FL-500S or PH10575",
        key="part_number",
    )

    button_col1, button_col2 = st.columns([1, 1], gap="small")

    with button_col1:
        search_clicked = st.button("🔎 Search Interchange Database")

    with button_col2:
        st.button("↻ Clear Filters", on_click=reset_filters)


if search_clicked:
    with st.spinner("Searching interchange database..."):
        results = search_parts(
            part_number=part_number.strip(),
            year=selected_year if selected_year != "All Years" else None,
            make=selected_make if selected_make != "All Makes" else None,
            model=selected_model if selected_model != "All Models" else None,
        )

    with st.container(border=True):
        if not results.empty:
            result_col1, result_col2, result_col3 = st.columns([5, 1, 1])

            with result_col1:
                st.success(f"Found {len(results)} matching records.")

            csv = results.to_csv(index=False).encode("utf-8")

            with result_col2:
                st.download_button(
                    label="⬇ Export CSV",
                    data=csv,
                    file_name="interchange_search_results.csv",
                    mime="text/csv",
                )

            with result_col3:
                st.button("⧉ Copy Results")

            mobile_results = results[
                [
                    "Part Type",
                    "OE Part Number",
                    "Cross Reference Brand",
                    "Cross Reference Part Number",
                    "Year",
                    "Make",
                    "Model",
                ]
            ]

            st.dataframe(mobile_results, width="stretch", hide_index=True)
        else:
            st.warning("No matching records found.")
else:
    st.info("Enter a part number or select vehicle filters to begin.")


st.html("""
<div class="footer">
    Built by Lyzatech • Prototype Interchange Intelligence Platform
</div>
""")