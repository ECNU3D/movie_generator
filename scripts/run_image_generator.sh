#!/bin/bash
# Launch the AI Image Generator Test App

# Change to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run src/image_generator/app.py --server.port 8503
