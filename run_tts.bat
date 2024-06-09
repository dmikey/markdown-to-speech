@echo off
call .venv\Scripts\activate.bat
echo Select an option:
echo 1: Run tts.py
echo 2: exit
set /p choice=Enter your choice (1/2):
if %choice%==1 (
    python tts.py
    pause
) else if %choice%==2 (
    exit
) else (
    echo Invalid choice. Please enter 1 or 2.
    pause
)
