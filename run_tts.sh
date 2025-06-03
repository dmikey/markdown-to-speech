#!/bin/bash

source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "Starting Markdown to Speech Converter (Streamlit)..."
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run tts_streamlit.py
