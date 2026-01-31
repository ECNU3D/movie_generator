#!/bin/bash
# Launch the AI Story Generator

# Change to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run src/story_generator/app.py --server.port 8502
