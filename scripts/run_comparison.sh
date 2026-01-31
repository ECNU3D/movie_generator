#!/bin/bash
# Launch the Video Generation Comparison Tool

# Change to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run src/comparison/app.py --server.port 8501
