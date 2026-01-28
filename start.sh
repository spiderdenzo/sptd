#!/bin/bash

echo "Starting Facebook Auto Messenger V3 for Streamlit..."

# Install dependencies
pip install -r requirements.txt --quiet

# Create directories
mkdir -p facebook_screenshots

# Check if running in Streamlit Cloud
if [ -n "$STREAMLIT_RUNTIME_ENVIRONMENT" ]; then
    echo "Running in Streamlit Cloud - using streamlit_app.py"
    # Streamlit will handle the app automatically
else
    echo "Running locally - you can use either:"
    echo "1. streamlit run streamlit_app.py (for UI)"
    echo "2. python main.py (for command line)"
fi
