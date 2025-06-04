# TTS - Markdown to Speech Converter

A modern web-based application that converts Markdown content into high-quality speech audio files using Google Text-to-Speech (gTTS) and optional AI optimization with OpenAI GPT-4o.

## Overview

- **Web Interface**: User-friendly Streamlit web application accessible via browser
- **File Upload & Text Input**: Upload .md files or paste content directly into the web interface
- **AI-Powered Optimization**: Optional GPT-4o integration to optimize text for natural speech synthesis
- **Multi-Language Support**: Convert text to speech in 11 different languages
- **Smart Caching**: Automatically caches AI-optimized content to reduce API costs
- **Progress Tracking**: Real-time progress bars and status updates during conversion
- **Audio Preview**: Built-in audio player to preview generated speech
- **Direct Download**: One-click download of generated MP3 files
- **Customizable Filtering**: Remove unwanted markdown symbols and characters

## Features

### Core Functionality
- Convert Markdown (.md) files to spoken audio (.mp3)
- Clean HTML/Markdown formatting for natural speech
- Chunked processing for large documents
- FFmpeg-based audio file concatenation

### AI Enhancement (Optional)
- GPT-4o text optimization for speech synthesis
- Automatic abbreviation expansion
- Number-to-word conversion
- Technical term pronunciation guides
- Natural pause insertion
- Secure API key storage with encryption

### User Interface
- Modern, responsive web interface
- File drag-and-drop support
- Real-time content preview
- Side-by-side original vs optimized content comparison
- Manual content editing capabilities

## Requirements

- **Python 3.x** (3.8+ recommended)
- **FFmpeg** (for audio file concatenation)
- **OpenAI API Key** (optional, for AI optimization)

## Installation

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd TTS
   ```

2. **Run the setup script:**
   ```bash
   # On macOS/Linux
   chmod +x run_tts.sh
   ./run_tts.sh
   
   # The script will automatically:
   # - Create a Python virtual environment
   # - Install all required dependencies
   # - Start the Streamlit web application
   ```

3. **Access the application:**
   - Open your browser to `http://localhost:8501`
   - The application will start automatically

### Manual Installation

If you prefer to set up manually:

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**

#### macOS
```bash
# Using Homebrew
brew install ffmpeg
```

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

#### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL/Fedora
sudo dnf install ffmpeg  # or: sudo yum install ffmpeg
```

4. **Start the application:**
   ```bash
   streamlit run tts_streamlit.py
   ```

## Usage

### Getting Started

1. **Launch the application** by running `./run_tts.sh` or `streamlit run tts_streamlit.py`
2. **Open your browser** to `http://localhost:8501`
3. **Upload or paste content:**
   - Upload a `.md` file using the file uploader, or
   - Paste Markdown content directly into the text area

### Basic Conversion

1. **Configure settings** in the sidebar:
   - Select your preferred language (11 languages supported)
   - Adjust chunk size for processing large documents
   - Choose symbols/characters to exclude from speech

2. **Add content:**
   - Upload a Markdown file, or
   - Paste content into the text area

3. **Convert to speech:**
   - Click "🎵 Convert to Speech"
   - Wait for processing (progress bar shows status)
   - Download the generated MP3 file

### AI-Enhanced Conversion (Optional)

For more natural-sounding speech:

1. **Add OpenAI API Key:**
   - Enter your OpenAI API key in the sidebar
   - Click the save button (💾) to store it securely

2. **Enable optimization:**
   - Check "Optimize text for speech using GPT-4o"
   - The AI will automatically optimize your content for better speech synthesis

3. **Review and convert:**
   - Compare original vs. optimized content
   - Make manual edits if needed
   - Click "🎵 Proceed with Conversion"

### Features in Detail

- **Smart Caching**: AI-optimized content is cached to avoid repeat API calls
- **Content Comparison**: Side-by-side view of original vs. optimized content
- **Manual Editing**: Edit optimized content before final conversion
- **Progress Tracking**: Real-time status updates and progress bars
- **Audio Preview**: Built-in player to preview generated speech
- **Secure Storage**: API keys are encrypted and stored locally

## Supported Languages

- English
- German
- French
- Spanish
- Italian
- Portuguese
- Dutch
- Russian
- Chinese (Simplified)
- Japanese
- Korean

## Configuration

### OpenAI API Key (Optional)

To use AI optimization features:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Enter it in the sidebar of the web application
3. Click the save button (💾) to store securely
4. The key is encrypted and stored locally on your machine

### Settings

- **Language**: Choose from 11 supported languages
- **Chunk Size**: Adjust for large documents (500-5000 characters)
- **Symbol Exclusion**: Remove specific markdown symbols from speech
- **AI Optimization**: Toggle GPT-4o enhancement on/off

## File Structure

```
TTS/
├── tts_streamlit.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
├── run_tts.sh             # Setup and launch script
├── README.md              # This file
├── test_content.md        # Sample content for testing
├── .gitignore             # Git ignore patterns
├── .venv/                 # Virtual environment (created on first run)
├── .api_key.enc           # Encrypted API key storage (optional)
└── .optimization_cache/   # AI optimization cache (optional)
```

## Dependencies

### Core Dependencies
- `streamlit>=1.39.0` - Web application framework
- `gtts==2.5.4` - Google Text-to-Speech
- `markdown==3.8` - Markdown to HTML conversion
- `beautifulsoup4==4.13.4` - HTML parsing and text extraction
- `cryptography>=3.4.8` - API key encryption
- `urllib3==1.26.20` - HTTP client

### Optional Dependencies
- `openai>=1.0.0` - AI optimization features

### System Dependencies
- `ffmpeg` - Audio file concatenation

## Troubleshooting

### Common Issues

**"FFmpeg not found"**
- Ensure FFmpeg is installed and in your system PATH
- Test with: `ffmpeg -version`

**"OpenAI library not available"**
- Install with: `pip install openai`
- Or use the application without AI optimization

**"API key not working"**
- Verify your OpenAI API key is valid
- Check your account has available credits
- Try deleting and re-entering the key

**Audio files not combining**
- Check FFmpeg installation
- Ensure sufficient disk space
- Try with smaller chunk sizes

### Performance Tips

- Use larger chunk sizes (3000-5000) for faster processing
- Enable AI optimization only when needed (uses API credits)
- Clear optimization cache periodically to save disk space

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Contributors

- [@bjarnepw](https://github.com/bjarnepw) - Original creator
- [@derekanderson](https://github.com/derekanderson) - Streamlit web interface and AI optimization

## Changelog

### v2.0.0 (Current)
- Complete rewrite with Streamlit web interface
- Added OpenAI GPT-4o integration for text optimization
- Secure API key storage with encryption
- Smart caching system for optimized content
- Real-time progress tracking
- Built-in audio preview and download
- Multi-language support expansion

### v1.0.0 (Legacy)
- Command-line interface
- Basic markdown to speech conversion
- Manual file selection prompts
