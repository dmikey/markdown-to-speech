#!/bin/bash

source .venv/bin/activate
echo "Select an option:"
echo "1: Run tts.py"
echo "2: Exit"
read -p "Enter your choice (1/2): " choice

if [ "$choice" = "1" ]; then
    python tts.py
    read -p "Press Enter to continue..."
elif [ "$choice" = "2" ]; then
    exit
else
    echo "Invalid choice. Please enter 1 or 2."
    read -p "Press Enter to continue..."
fi
