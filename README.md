# TTS

TTS (Text-to-Speech) is a Python script designed to convert markdown files into spoken audio files. It utilizes the gTTS (Google Text-to-Speech) library for text-to-speech conversion.

## Overview

- Converts markdown files (.md) into spoken audio files (.mp3).
- Provides options to select language and exclude certain characters/symbols from the audio output.
- Utilizes a progress bar to indicate the conversion progress.
- Handles markdown formatting such as tables and code blocks gracefully.

## Requirements

- Python 3.x
- ffmpeg (for audio file concatenation)

## Installation

### Python:

#### Windows:
1. Download the latest version of Python from the [official Python website](https://www.python.org/downloads/windows/).
2. Run the installer and follow the on-screen instructions. Make sure to check the box that says "Add Python X.X to PATH" during installation.

#### Linux:
1. Most Linux distributions come with Python pre-installed. You can check if Python is installed by running the following command in the terminal:
   ```
   python3 --version
   ```
2. If Python is not installed, you can install it using your package manager. For example, on Debian-based systems (like Ubuntu), you can use:
   ```
   sudo apt update
   sudo apt install python3
   ```

### ffmpeg:

#### Windows:
1. Download the ffmpeg binaries for Windows from the [official ffmpeg website](https://ffmpeg.org/download.html).
2. Extract the downloaded zip file to a location on your computer.
3. Add the path to the `bin` directory of ffmpeg to the system PATH environment variable. Follow these steps:
   - Right-click on "This PC" or "My Computer" and select "Properties."
   - Click on "Advanced system settings."
   - In the System Properties window, click on the "Environment Variables" button.
   - Under "System variables," find the "Path" variable and click "Edit."
   - Add the path to the `bin` directory of ffmpeg (e.g., `C:\ffmpeg\bin`) to the list of paths.
   - Click "OK" to save the changes.
4. To check if ffmpeg is added to the PATH, open a command prompt and type:
```
ffmpeg -version
```

#### Linux:
1. Install ffmpeg using your package manager. For example, on Debian-based systems (like Ubuntu), you can use:
   ```
   sudo apt update
   sudo apt install ffmpeg
   ```

## Usage

1. Clone or download the repository to your local machine.
2. Open a terminal or command prompt and navigate to the project directory.
3. Run the script `run_tts.sh` (for Linux) or `run_tts.bat` (for Windows).
4. Follow the on-screen instructions to select an option:
    - Option 1: Run `tts.py` to convert markdown files to spoken audio.
    - Option 2: Exit the script.

## How to Use

1. Launch the script.
2. Select a markdown file (.md) using the on-screen prompts.
3. Choose the desired language and select checkboxes to exclude specific characters/symbols.
4. Follow the prompts to complete the conversion process.
5. Once the conversion is finished, the audio file will be saved in the same directory as the input markdown file.

## Contributors

- [@bjarnepw](https://github.com/bjarnepw)
