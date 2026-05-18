# Automotive Part Interchange Database

Prototype automotive interchange database for cross-referencing OE, OEM, and aftermarket automotive parts across multiple vehicle applications.

---

## Features

- Search by OE part number
- Search by aftermarket number
- Vehicle fitment lookup
- SQLite relational database
- Streamlit search interface

---

## Tech Stack

- Python
- SQLite
- Pandas
- Streamlit

---

## Database Structure

### Tables
- vehicles
- parts
- cross_references
- fitment

---

## Application Preview

![Search Results](assets/search-results.png)

---

## Running the Application

```bash
pip install -r requirements.txt
streamlit run src/app.py