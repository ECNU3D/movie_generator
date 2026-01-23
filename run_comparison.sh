#!/bin/bash
# Launch the Video Generation Comparison Tool

# Activate virtual environment
source venv/bin/activate

# Change to project root
cd "$(dirname "$0")"

# Run Streamlit app
streamlit run src/comparison/app.py --server.port 8501
