#!/bin/bash
# Launch the AI Story Generator

# Activate virtual environment
source venv/bin/activate

# Change to project root
cd "$(dirname "$0")"

# Run Streamlit app
streamlit run src/story_generator/app.py --server.port 8502
