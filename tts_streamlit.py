import streamlit as st
import markdown
from gtts import gTTS
import os
import tempfile
from bs4 import BeautifulSoup
import time

# Supported languages
LANGUAGES = {
    "English": "en",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko"
}

# Signs to exclude
SIGNS = {
    "Pipes (|)": "|",
    "Hyphens (-)": "-",
    "Equals (=)": "=",
    "Double Underscores (__)": "__",
    "Backticks (`)": "`",
    "Asterisks (*)": "*",
    "Hashes (#)": "#",
    "Exclamation Marks (!)": "!",
    "Square Brackets ([])": "[]",
    "Parentheses (())": "()",
}

def clean_text(text, signs_to_exclude):
    """Remove unwanted Markdown elements by replacing them with appropriate text or removing them"""
    replacements = [
        ("|", ""),       # Remove pipe characters from tables
        ("-", " "),      # Replace hyphens with spaces
        ("=", " "),      # Replace equal signs with spaces
        ("__", " "),     # Replace double underscores with spaces
        ("`", ""),       # Remove backticks
        ("*", ""),       # Remove asterisks
        ("#", ""),       # Remove hashes
        ("!", ""),       # Remove exclamation marks
        ("[", ""),       # Remove square brackets
        ("]", ""),       # Remove square brackets
        ("(", ""),       # Remove parentheses
        (")", ""),       # Remove parentheses
    ]
    
    for old, new in replacements:
        if old in signs_to_exclude:
            text = text.replace(old, new)
    
    return text

def combine_audio_chunks(temp_files, output_file):
    """Combine MP3 files using ffmpeg"""
    try:
        file_list = '|'.join(temp_files)
        command = f'ffmpeg -i "concat:{file_list}" -acodec copy "{output_file}" -y'
        os.system(command)
        return True
    except Exception as e:
        st.error(f"Error during concatenation: {e}")
        return False

def markdown_to_speech(md_file_content, output_file, lang, chunk_size, signs_to_exclude, progress_bar, status_text):
    """Convert markdown to speech with progress tracking"""
    try:
        # Update status
        status_text.text("Reading markdown content...")
        time.sleep(0.1)  # Small delay for UI update
        
        # Convert markdown to HTML
        status_text.text("Converting markdown to HTML...")
        progress_bar.progress(10)
        html_text = markdown.markdown(md_file_content)
        
        # Convert HTML to plain text
        status_text.text("Extracting text from HTML...")
        progress_bar.progress(20)
        soup = BeautifulSoup(html_text, "html.parser")
        plain_text = ''.join(soup.find_all(string=True))
        
        # Clean the extracted text
        status_text.text("Cleaning text...")
        progress_bar.progress(30)
        cleaned_text = clean_text(plain_text, signs_to_exclude)

        # Split text into chunks to handle gTTS limits
        text_chunks = [cleaned_text[i:i + chunk_size] for i in range(0, len(cleaned_text), chunk_size)]
        total_chunks = len(text_chunks)
        
        status_text.text(f"Processing {total_chunks} chunks...")
        progress_bar.progress(35)
        
        # Convert each chunk to speech and save as a temporary file
        temp_files = []
        for i, chunk in enumerate(text_chunks):
            current_chunk = i + 1
            status_text.text(f"Converting chunk {current_chunk} of {total_chunks}...")
            
            # Calculate progress (35% to 80% for chunk processing)
            chunk_progress = 35 + int((current_chunk / total_chunks) * 45)
            progress_bar.progress(chunk_progress)
            
            tts = gTTS(chunk, lang=lang)
            temp_file = f"{output_file}_part_{i}.mp3"
            tts.save(temp_file)
            temp_files.append(temp_file)
        
        # Combine all temporary files into a single output file
        status_text.text("Combining audio files...")
        progress_bar.progress(85)
        success = combine_audio_chunks(temp_files, output_file)
        
        if not success:
            return False
        
        # Clean up temporary files
        status_text.text("Cleaning up temporary files...")
        progress_bar.progress(95)
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Complete
        progress_bar.progress(100)
        status_text.text(f"✅ Conversion complete! Audio saved as {os.path.basename(output_file)}")
        return True
        
    except Exception as e:
        status_text.text(f"❌ Error during conversion: {str(e)}")
        progress_bar.progress(0)
        return False

def main():
    st.set_page_config(
        page_title="Markdown to Speech Converter",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 Markdown to Speech Converter")
    st.markdown("Convert your Markdown files to high-quality speech audio using Google Text-to-Speech")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        selected_language = st.selectbox(
            "Select Language:",
            options=list(LANGUAGES.keys()),
            index=0
        )
        
        # Chunk size
        chunk_size = st.slider(
            "Chunk Size (characters):",
            min_value=500,
            max_value=5000,
            value=1000,
            step=100,
            help="Larger chunks = fewer API calls but may hit rate limits"
        )
        
        # Signs to exclude
        st.subheader("🚫 Exclude Signs")
        signs_to_exclude = []
        for sign_text, sign in SIGNS.items():
            if st.checkbox(sign_text, key=f"exclude_{sign}"):
                signs_to_exclude.append(sign)
    
    # Initialize session state for file content
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📄 Upload Markdown File")
        uploaded_file = st.file_uploader(
            "Choose a Markdown file",
            type=['md', 'markdown', 'txt'],
            help="Upload a .md file to convert to speech"
        )
        
        # Store file content in session state when file is uploaded
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode('utf-8')
            st.session_state.file_content = file_content
            st.session_state.filename = uploaded_file.name
        
        # Text area for direct input
        st.subheader("Or paste Markdown content:")
        markdown_text = st.text_area(
            "Markdown Content",
            height=300,
            placeholder="Paste your markdown content here..."
        )
    
    with col2:
        st.header("🎯 Preview")
        if st.session_state.file_content is not None:
            preview_content = st.session_state.file_content
            st.text_area("File Preview", value=preview_content[:500] + "..." if len(preview_content) > 500 else preview_content, height=200, disabled=True)
        elif markdown_text:
            st.text_area("Text Preview", value=markdown_text[:500] + "..." if len(markdown_text) > 500 else markdown_text, height=200, disabled=True)
        else:
            st.info("Upload a file or paste text to see preview")
    
    # Convert button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎵 Convert to Speech", type="primary", use_container_width=True):
            # Get content
            content = None
            filename = None
            
            if st.session_state.file_content is not None:
                content = st.session_state.file_content
                filename = st.session_state.filename
            elif markdown_text.strip():
                content = markdown_text
                filename = "markdown_text.md"
            
            if content:
                # Create output filename
                base_name = os.path.splitext(filename)[0]
                output_file = f"{base_name}.mp3"
                
                # Show conversion progress
                st.subheader("🔄 Conversion Progress")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Convert to speech
                lang_code = LANGUAGES[selected_language]
                success = markdown_to_speech(
                    content, 
                    output_file, 
                    lang_code, 
                    chunk_size, 
                    signs_to_exclude,
                    progress_bar,
                    status_text
                )
                
                if success and os.path.exists(output_file):
                    st.success("🎉 Conversion completed successfully!")
                    
                    # Provide download button
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="📥 Download Audio File",
                            data=file.read(),
                            file_name=output_file,
                            mime="audio/mpeg",
                            type="primary"
                        )
                    
                    # Show audio player
                    st.audio(output_file)
                    
                    # Clean up the file after offering download
                    # Note: In production, you might want to keep files for a while
                else:
                    st.error("❌ Conversion failed. Please check your input and try again.")
            else:
                st.warning("⚠️ Please upload a file or paste some markdown content to convert.")

if __name__ == "__main__":
    main()
