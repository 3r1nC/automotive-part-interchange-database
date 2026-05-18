#!/bin/bash

echo "Activating virtual environment..."

source venv/Scripts/activate

echo "Installing/updating dependencies..."

pip install -r requirements.txt

echo "Starting Streamlit app..."

python -m streamlit run src/app.py