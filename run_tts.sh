#!/bin/bash

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment. Make sure python3 is installed."
        exit 1
    fi
    echo "✅ Virtual environment created successfully!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Install/update requirements
echo "Installing/updating requirements..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
python3 -m pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Warning: Some packages may have failed to install. Check your requirements.txt file."
fi

echo ""
echo "Starting Markdown to Speech Converter (Streamlit)..."
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run tts_streamlit.py
