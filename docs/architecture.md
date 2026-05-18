# System Architecture

## Project Overview

The Automotive Part Interchange Database is a prototype application designed to help users identify compatible automotive parts across multiple vehicles.

The system allows users to search OE, OEM, and aftermarket part numbers and view related vehicle fitment information.

---

## Architecture Summary

The application uses a lightweight local architecture:

```text
CSV Sample Data
      ↓
Python Import Script
      ↓
SQLite Database
      ↓
Python Query Logic
      ↓
Streamlit User Interface