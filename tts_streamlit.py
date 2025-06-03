import streamlit as st
import markdown
from gtts import gTTS
import os
import tempfile
import subprocess
import shutil
from bs4 import BeautifulSoup
import time
import json
import base64
import socket
import hashlib
import logging
from cryptography.fernet import Fernet

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
    logger.info("OpenAI library loaded successfully")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

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

# API Key storage functions
def get_key_file_path():
    """Get the path for storing the encrypted API key"""
    return os.path.join(os.path.dirname(__file__), '.api_key.enc')

def get_or_create_encryption_key():
    """Get or create an encryption key based on machine characteristics"""
    # Create a machine-specific key based on current working directory and hostname
    machine_id = f"{socket.gethostname()}_{os.getcwd()}"
    key_seed = hashlib.sha256(machine_id.encode()).digest()
    return base64.urlsafe_b64encode(key_seed)

def save_api_key(api_key):
    """Save the API key encrypted to a local file"""
    try:
        encryption_key = get_or_create_encryption_key()
        fernet = Fernet(encryption_key)
        encrypted_key = fernet.encrypt(api_key.encode())
        
        key_file = get_key_file_path()
        with open(key_file, 'wb') as f:
            f.write(encrypted_key)
        return True
    except Exception as e:
        st.error(f"Error saving API key: {str(e)}")
        return False

def load_api_key():
    """Load and decrypt the API key from the local file"""
    try:
        key_file = get_key_file_path()
        if not os.path.exists(key_file):
            return None
        
        encryption_key = get_or_create_encryption_key()
        fernet = Fernet(encryption_key)
        
        with open(key_file, 'rb') as f:
            encrypted_key = f.read()
        
        decrypted_key = fernet.decrypt(encrypted_key).decode()
        return decrypted_key
    except Exception as e:
        # If decryption fails, remove the corrupted file
        key_file = get_key_file_path()
        if os.path.exists(key_file):
            try:
                os.remove(key_file)
            except:
                pass
        return None

def delete_stored_api_key():
    """Delete the stored API key file"""
    try:
        key_file = get_key_file_path()
        if os.path.exists(key_file):
            os.remove(key_file)
        return True
    except Exception as e:
        st.error(f"Error deleting stored API key: {str(e)}")
        return False

# Cache functions for optimized content
def get_cache_dir():
    """Get or create the cache directory for optimized content"""
    cache_dir = os.path.join(os.path.dirname(__file__), '.optimization_cache')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def get_content_hash(content):
    """Generate a hash for the markdown content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def save_optimized_content(content_hash, optimized_content):
    """Save optimized content to cache"""
    try:
        cache_dir = get_cache_dir()
        cache_file = os.path.join(cache_dir, f"{content_hash}.json")
        
        cache_data = {
            "timestamp": time.time(),
            "optimized_content": optimized_content,
            "version": "1.0"  # For future compatibility
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.warning(f"Could not save optimized content to cache: {str(e)}")
        return False

def load_optimized_content(content_hash):
    """Load optimized content from cache if it exists"""
    try:
        cache_dir = get_cache_dir()
        cache_file = os.path.join(cache_dir, f"{content_hash}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache is recent (within 30 days)
        cache_age = time.time() - cache_data.get("timestamp", 0)
        if cache_age > (30 * 24 * 60 * 60):  # 30 days in seconds
            # Remove old cache file
            os.remove(cache_file)
            return None
        
        return cache_data.get("optimized_content")
        
    except Exception as e:
        # If there's an error reading the cache, remove the corrupted file
        try:
            cache_file = os.path.join(get_cache_dir(), f"{content_hash}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        except:
            pass
        return None

def clear_optimization_cache():
    """Clear all cached optimized content"""
    try:
        cache_dir = get_cache_dir()
        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(cache_dir, filename)
                    os.remove(file_path)
        return True
    except Exception as e:
        st.error(f"Error clearing cache: {str(e)}")
        return False

def get_cache_stats():
    """Get cache statistics"""
    try:
        cache_dir = get_cache_dir()
        if not os.path.exists(cache_dir):
            return {"count": 0, "total_size": 0}
        
        count = 0
        total_size = 0
        
        for filename in os.listdir(cache_dir):
            if filename.endswith('.json'):
                count += 1
                file_path = os.path.join(cache_dir, filename)
                total_size += os.path.getsize(file_path)
        
        return {"count": count, "total_size": total_size}
    except:
        return {"count": 0, "total_size": 0}

def optimize_for_speech(content, api_key, progress_callback=None):
    """Optimize markdown content for better speech synthesis using OpenAI GPT-4o with caching"""
    if not OPENAI_AVAILABLE:
        st.error("OpenAI library not installed. Run: pip install openai")
        return content
    
    try:
        # Check cache first
        content_hash = get_content_hash(content)
        cached_content = load_optimized_content(content_hash)
        
        if cached_content:
            if progress_callback:
                progress_callback("✅ Found optimized content in cache!", 100)
            st.info("🚀 Using cached optimized content (no API call needed)")
            return cached_content
        
        # If not in cache, proceed with OpenAI optimization
        if progress_callback:
            progress_callback("Connecting to OpenAI API...", 5)
        
        client = openai.OpenAI(api_key=api_key)
        
        # Calculate chunk size (aim for ~3000 characters to leave room for prompt)
        max_chunk_size = 3000
        content_chunks = []
        
        # Split content into chunks
        for i in range(0, len(content), max_chunk_size):
            chunk = content[i:i + max_chunk_size]
            content_chunks.append(chunk)
        
        total_chunks = len(content_chunks)
        optimized_chunks = []
        
        prompt = """You are an expert at converting written text to speech-friendly format. 

Please optimize the following markdown content for text-to-speech conversion by:
1. Expanding abbreviations and acronyms 
2. Converting numbers to written form (e.g., "123" to "one hundred twenty-three")
3. Adding pronunciation guides for technical terms in parentheses
4. Converting symbols and special characters to spoken words
5. Adding natural pauses with commas and periods
6. Removing or converting markdown formatting that doesn't translate well to speech
7. Making sentences flow more naturally when spoken aloud
8. Converting URLs to "link" or describing their purpose
9. Handling code blocks by describing what they do instead of reading code syntax

Keep the core meaning and content intact, but make it sound natural when read aloud.
Return ONLY the optimized text without any additional commentary.

Content to optimize:
"""

        # Process each chunk
        for i, chunk in enumerate(content_chunks):
            if progress_callback:
                progress = 10 + int((i / total_chunks) * 80)  # 10% to 90% for processing
                progress_callback(f"Optimizing chunk {i + 1} of {total_chunks}...", progress)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at optimizing text for speech synthesis. Return only the optimized text."},
                    {"role": "user", "content": prompt + chunk}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            optimized_chunks.append(response.choices[0].message.content)
        
        # Combine all optimized chunks
        optimized_content = "\n".join(optimized_chunks)
        
        # Save to cache
        if progress_callback:
            progress_callback("Saving to cache...", 95)
        
        if save_optimized_content(content_hash, optimized_content):
            st.success("💾 Optimized content saved to cache for future use!")
        
        if progress_callback:
            progress_callback("Optimization complete!", 100)
        
        return optimized_content
        
    except Exception as e:
        st.error(f"Error optimizing content with OpenAI: {str(e)}")
        return content

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
    """Combine MP3 files using ffmpeg with better error handling"""
    try:
        if len(temp_files) == 1:
            # If only one file, just rename it
            shutil.move(temp_files[0], output_file)
            return True
        
        # Create a temporary file list for ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for temp_file in temp_files:
                f.write(f"file '{temp_file}'\n")
            filelist_path = f.name
        
        try:
            # Use ffmpeg with file list for more reliable concatenation
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path,
                '-c', 'copy', output_file, '-y'
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                st.error(f"FFmpeg error: {result.stderr}")
                return False
                
        finally:
            # Clean up the temporary file list
            if os.path.exists(filelist_path):
                os.remove(filelist_path)
        
    except FileNotFoundError:
        st.error("FFmpeg not found. Please install FFmpeg to combine audio files.")
        return False
    except Exception as e:
        st.error(f"Error during concatenation: {e}")
        return False

def markdown_to_speech(md_file_content, output_file, lang, chunk_size, signs_to_exclude, progress_bar, status_text):
    """Convert markdown to speech with progress tracking"""
    logger.info(f"=== markdown_to_speech STARTED ===")
    logger.info(f"Content length: {len(md_file_content)}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Language: {lang}")
    logger.info(f"Chunk size: {chunk_size}")
    
    temp_files = []  # Initialize temp_files list outside try block
    try:
        # Update status
        status_text.text("Reading markdown content...")
        logger.info("Step 1: Reading markdown content")
        time.sleep(0.1)  # Small delay for UI update
        
        # Convert markdown to HTML
        status_text.text("Converting markdown to HTML...")
        progress_bar.progress(10)
        logger.info("Step 2: Converting markdown to HTML")
        html_text = markdown.markdown(md_file_content)
        logger.info(f"HTML conversion complete. HTML length: {len(html_text)}")
        
        # Convert HTML to plain text
        status_text.text("Extracting text from HTML...")
        progress_bar.progress(20)
        logger.info("Step 3: Extracting plain text from HTML")
        soup = BeautifulSoup(html_text, "html.parser")
        plain_text = ''.join(soup.find_all(string=True))
        logger.info(f"Plain text extraction complete. Text length: {len(plain_text)}")
        
        # Clean the extracted text
        status_text.text("Cleaning text...")
        progress_bar.progress(30)
        logger.info("Step 4: Cleaning text")
        cleaned_text = clean_text(plain_text, signs_to_exclude)
        logger.info(f"Text cleaning complete. Cleaned text length: {len(cleaned_text)}")

        # Split text into chunks to handle gTTS limits
        text_chunks = [cleaned_text[i:i + chunk_size] for i in range(0, len(cleaned_text), chunk_size)]
        total_chunks = len(text_chunks)
        logger.info(f"Step 5: Text split into {total_chunks} chunks")
        
        status_text.text(f"Processing {total_chunks} chunks...")
        progress_bar.progress(35)
        
        # Convert each chunk to speech and save as a temporary file
        for i, chunk in enumerate(text_chunks):
            current_chunk = i + 1
            status_text.text(f"Converting chunk {current_chunk} of {total_chunks}...")
            logger.info(f"Processing chunk {current_chunk}/{total_chunks} (length: {len(chunk)})")
            
            # Calculate progress (35% to 80% for chunk processing)
            chunk_progress = 35 + int((current_chunk / total_chunks) * 45)
            progress_bar.progress(chunk_progress)
            
            try:
                tts = gTTS(chunk, lang=lang)
                temp_file = f"{output_file}_part_{i}.mp3"
                logger.info(f"Creating temporary file: {temp_file}")
                tts.save(temp_file)
                temp_files.append(temp_file)
                logger.info(f"Chunk {current_chunk} saved successfully")
            except Exception as chunk_error:
                logger.error(f"Error processing chunk {current_chunk}: {chunk_error}")
                raise chunk_error
        
        # Combine all temporary files into a single output file
        status_text.text("Combining audio files...")
        progress_bar.progress(85)
        logger.info(f"Step 6: Combining {len(temp_files)} temporary files into {output_file}")
        success = combine_audio_chunks(temp_files, output_file)
        logger.info(f"Audio combination result: {success}")
        
        if not success:
            # Clean up temporary files before returning False
            status_text.text("Cleaning up temporary files after error...")
            logger.error("Audio combination failed, cleaning up temporary files")
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        logger.info(f"Removed temporary file: {temp_file}")
                    except Exception:
                        logger.warning(f"Failed to remove temporary file: {temp_file}")
            return False
        
        # Clean up temporary files after successful combination
        status_text.text("Cleaning up temporary files...")
        progress_bar.progress(95)
        logger.info("Step 7: Cleaning up temporary files")
        cleanup_success = True
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.info(f"Removed temporary file: {temp_file}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not delete temporary file {temp_file}: {cleanup_error}")
                    st.warning(f"Warning: Could not delete temporary file {temp_file}: {cleanup_error}")
                    cleanup_success = False
        
        # Complete
        progress_bar.progress(100)
        final_file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
        logger.info(f"=== CONVERSION COMPLETE ===")
        logger.info(f"Output file: {output_file}")
        logger.info(f"File size: {final_file_size} bytes")
        logger.info(f"Cleanup successful: {cleanup_success}")
        
        if cleanup_success:
            status_text.text(f"✅ Conversion complete! Audio saved as {os.path.basename(output_file)}")
        else:
            status_text.text(f"✅ Conversion complete! Audio saved as {os.path.basename(output_file)} (some temporary files may remain)")
        return True
        
    except Exception as e:
        # Ensure cleanup happens even if there's an error
        logger.error(f"=== CONVERSION FAILED ===")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        status_text.text(f"❌ Error during conversion: {str(e)}")
        progress_bar.progress(0)
        
        # Clean up any temporary files that were created
        if temp_files:
            logger.info(f"Cleaning up {len(temp_files)} temporary files after error")
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        logger.info(f"Removed temporary file after error: {temp_file}")
                    except Exception:
                        logger.warning(f"Failed to remove temporary file after error: {temp_file}")
        
        return False

def main():
    logger.info("=== MAIN FUNCTION STARTED ===")
    logger.info(f"Session state keys at start: {list(st.session_state.keys())}")
    
    st.set_page_config(
        page_title="Markdown to Speech Converter",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 Markdown to Speech Converter")
    st.markdown("Convert your Markdown files to high-quality speech audio using Google Text-to-Speech")
    
    logger.info("Starting sidebar configuration...")
    
    # Sidebar for settings - MOVED TO TOP TO DEFINE VARIABLES FIRST
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # OpenAI API Key section
        st.subheader("🤖 AI Optimization (Optional)")
        
        if OPENAI_AVAILABLE:
            # Load stored API key
            stored_api_key = load_api_key()
            
            # Initialize session state for API key
            if 'api_key_input' not in st.session_state:
                st.session_state.api_key_input = stored_api_key or ""
            
            # API Key input
            col1, col2 = st.columns([3, 1])
            
            with col1:
                api_key = st.text_input(
                    "OpenAI API Key:",
                    value=st.session_state.api_key_input,
                    type="password",
                    help="Enter your OpenAI API key to use GPT-4o for optimizing text for speech",
                    key="api_key_field"
                )
            
            with col2:
                # Save button
                if st.button("💾", help="Save API key"):
                    if api_key.strip():
                        if save_api_key(api_key.strip()):
                            st.success("✅ Saved!")
                            st.session_state.api_key_input = api_key.strip()
                        else:
                            st.error("❌ Failed to save")
                    else:
                        st.warning("⚠️ Enter a key first")
            
            # Delete stored key option
            if stored_api_key:
                if st.button("🗑️ Delete Stored Key", help="Remove saved API key"):
                    if delete_stored_api_key():
                        st.success("✅ API key deleted")
                        st.session_state.api_key_input = ""
                        st.rerun()
            
            # Show status
            if stored_api_key:
                st.info("🔐 API key loaded from storage")
            
            # Auto-enable optimization if API key is available
            default_use_openai = bool(api_key and api_key.strip())
            
            use_openai = st.checkbox(
                "Optimize text for speech using GPT-4o",
                value=default_use_openai,
                help="Use AI to make the text more speech-friendly before conversion. Auto-enabled when API key is available.",
                disabled=not api_key
            )
            
            # Cache management section
            if use_openai or api_key:
                st.markdown("---")
                st.subheader("📦 Optimization Cache")
                
                cache_stats = get_cache_stats()
                cache_count = cache_stats["count"]
                cache_size_mb = cache_stats["total_size"] / (1024 * 1024)
                
                if cache_count > 0:
                    st.info(f"💾 Cached items: {cache_count} ({cache_size_mb:.1f} MB)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Clear Cache", help="Remove all cached optimizations"):
                            if clear_optimization_cache():
                                st.success("✅ Cache cleared!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to clear cache")
                    
                    with col2:
                        if st.button("📊 Cache Info", help="Show cache details"):
                            st.write(f"**Cache Statistics:**")
                            st.write(f"- Items: {cache_count}")
                            st.write(f"- Size: {cache_size_mb:.1f} MB")
                            st.write(f"- Location: `.optimization_cache/`")
                else:
                    st.info("💾 No cached optimizations yet")
        else:
            st.warning("⚠️ OpenAI library not installed")
            st.code("pip install openai", language="bash")
            use_openai = False
            api_key = None
        
        st.markdown("---")
        
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
    
    logger.info("Sidebar configuration completed")
    logger.info(f"Variables defined: selected_language={selected_language}, chunk_size={chunk_size}, use_openai={use_openai}")
    logger.info(f"signs_to_exclude={signs_to_exclude}")
    
    # Initialize session state for file content
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None

    logger.info("Session state initialized")
    logger.info(f"Checking for should_convert flag: {getattr(st.session_state, 'should_convert', False)}")
    
    # Check if any proceed button was clicked (look for proceed_conversion_* keys in session state)
    proceed_button_keys = [key for key in st.session_state.keys() if key.startswith('proceed_conversion_')]
    logger.info(f"Found proceed button keys in session state: {proceed_button_keys}")
    
    # Check if any of these buttons were just clicked (have True value)
    proceed_buttons_clicked = []
    for key in proceed_button_keys:
        value = st.session_state.get(key, False)
        logger.info(f"Button {key} has value: {value}")
        if value is True:
            proceed_buttons_clicked.append(key)
    
    logger.info(f"Proceed buttons clicked (True values): {proceed_buttons_clicked}")
    
    if proceed_buttons_clicked:
        logger.info(f"=== PROCEED BUTTON DETECTED IN SESSION STATE ===")
        # Find the most recent proceed button that was clicked
        latest_proceed_key = proceed_buttons_clicked[-1]  # Get the last one
        logger.info(f"Latest proceed button key: {latest_proceed_key}")
        
        # Reset the button state to prevent repeated triggers
        st.session_state[latest_proceed_key] = False
        
        # Trigger conversion by setting the conversion flag
        # We need to get the content from the manual_edit field or optimized content
        if 'manual_edit' in st.session_state:
            content = st.session_state.get('manual_edit', '')
            logger.info(f"Using manually edited content: {len(content)} characters")
        else:
            # Find the optimized content key that matches
            content_hash_from_button = latest_proceed_key.replace('proceed_conversion_', '')
            # Look for optimized content in session state
            optimized_content_keys = [key for key in st.session_state.keys() if key.startswith('optimized_content_')]
            if optimized_content_keys:
                content = st.session_state.get(optimized_content_keys[0], '')
                logger.info(f"Using optimized content from session state: {len(content)} characters")
            else:
                logger.error("No content found in session state!")
                content = ''
        
        if content and content.strip():
            logger.info("Setting conversion flag from proceed button detection...")
            st.session_state.should_convert = True
            st.session_state.conversion_content = content
            st.session_state.conversion_filename = getattr(st.session_state, 'filename', 'markdown_text.md')
            logger.info(f"Conversion triggered from proceed button:")
            logger.info(f"- Content length: {len(content)}")
            logger.info(f"- Filename: {st.session_state.conversion_filename}")
        else:
            logger.error("Cannot proceed with conversion: Content is empty")
            st.error("❌ Cannot proceed with conversion: Content is empty")

    # Check if we should proceed with conversion (from a previous run) - MOVED AFTER SIDEBAR
    if getattr(st.session_state, 'should_convert', False):
        logger.info("=== PROCEEDING WITH STORED CONVERSION ===")
        logger.info(f"Session state before clearing flag: should_convert={st.session_state.should_convert}")
        
        # Clear the conversion flag and use the stored content
        st.session_state.should_convert = False
        content = getattr(st.session_state, 'conversion_content', '')
        filename = getattr(st.session_state, 'conversion_filename', 'markdown_text.md')
        
        logger.info(f"Retrieved stored data:")
        logger.info(f"- Content length: {len(content)} characters")
        logger.info(f"- Filename: {filename}")
        logger.info(f"- Content preview: {content[:100]}..." if len(content) > 100 else f"- Full content: {content}")
        
        if not content:
            logger.error("CRITICAL: No content found in session state!")
            st.error("❌ No content found for conversion!")
            return
        
        logger.info(f"Proceeding with conversion - using stored content ({len(content)} chars)")
        st.success(f"🚀 Ready to convert! Using content: {len(content)} characters")
        
        # Create output filename
        base_name = os.path.splitext(filename)[0]
        output_file = f"{base_name}.mp3"
        logger.info(f"Output file will be: {output_file}")
        
        # Debug: Show what we're about to convert
        st.info(f"🔄 Starting conversion of {len(content)} characters to {output_file}")
        st.write(f"🔍 **Debug:** About to call markdown_to_speech with:")
        st.write(f"- Content length: {len(content)} chars")
        st.write(f"- Output file: {output_file}")
        st.write(f"- Language: {selected_language}")
        st.write(f"- Chunk size: {chunk_size}")
        st.write(f"- Signs to exclude: {signs_to_exclude}")
        
        # Show conversion progress
        st.subheader("🔄 Conversion Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Convert to speech
        lang_code = LANGUAGES[selected_language]
        logger.info(f"Starting TTS conversion with parameters:")
        logger.info(f"- lang_code: {lang_code}")
        logger.info(f"- chunk_size: {chunk_size}")
        logger.info(f"- signs_to_exclude: {signs_to_exclude}")
        logger.info(f"- output_file: {output_file}")
        
        try:
            logger.info("About to call markdown_to_speech function...")
            success = markdown_to_speech(
                content, 
                output_file, 
                lang_code, 
                chunk_size, 
                signs_to_exclude,
                progress_bar,
                status_text
            )
            logger.info(f"markdown_to_speech returned: {success}")
        except Exception as e:
            logger.error(f"Exception caught in main conversion: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception traceback:", exc_info=True)
            st.error(f"❌ Error during conversion: {str(e)}")
            success = False
        
        logger.info(f"Conversion function returned: {success}")
        logger.info(f"Output file exists: {os.path.exists(output_file)}")
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logger.info(f"Output file size: {file_size} bytes")
        
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logger.info(f"SUCCESS! Conversion completed successfully!")
            logger.info(f"- Output file: {output_file}")
            logger.info(f"- File size: {file_size} bytes")
            st.success("🎉 Conversion completed successfully!")
            st.write(f"🔍 **Debug:** File created successfully! Size: {file_size} bytes")
            
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
            logger.info("Download button and audio player displayed")
        else:
            logger.error("=== CONVERSION FAILED ===")
            logger.error(f"Success flag: {success}")
            logger.error(f"File exists: {os.path.exists(output_file)}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.error(f"File size: {file_size} bytes")
            else:
                logger.error("Output file does not exist")
            st.error("❌ Conversion failed. Please check your input and try again.")
            st.write("🔍 **Debug:** Conversion failed - check the logs above for details")
        
        # Stop execution after conversion attempt
        logger.info("Conversion attempt completed, stopping execution with return")
        logger.info("=== MAIN FUNCTION ENDING (CONVERSION PATH) ===")
        return
    
    logger.info("No conversion flag found, proceeding to main UI")
    # Main content area
    st.header("📄 Upload Markdown File or Enter Content")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a Markdown file (optional)",
        type=['md', 'markdown', 'txt'],
        help="Upload a .md file to auto-fill the content below"
    )
    
    # Store file content in session state when file is uploaded
    if uploaded_file is not None:
        file_content = uploaded_file.read().decode('utf-8')
        st.session_state.file_content = file_content
        st.session_state.filename = uploaded_file.name
        logger.info(f"File uploaded: {uploaded_file.name}, content length: {len(file_content)}")
    
    # Combined text area for file content or manual input
    # Use file content if available, otherwise empty
    initial_value = st.session_state.file_content if st.session_state.file_content else ""
    logger.info(f"Text area initial value length: {len(initial_value)}")
    
    markdown_text = st.text_area(
        "Markdown Content:",
        value=initial_value,
        height=400,
        placeholder="Upload a file above or paste your markdown content here...",
        help="This area will auto-fill when you upload a file, or you can type/paste content directly"
    )
    
    logger.info(f"Current markdown_text length: {len(markdown_text)}")
    
    # Convert button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
            if st.button("🎵 Convert to Speech", type="primary", use_container_width=True):
                logger.info("=== MAIN CONVERT BUTTON CLICKED ===")
                
                # Get content and filename
                content = markdown_text.strip() if markdown_text.strip() else None
                logger.info(f"Content extracted: {len(content) if content else 0} characters")
                
                # Determine filename
                if st.session_state.filename:
                    filename = st.session_state.filename
                    logger.info(f"Using uploaded filename: {filename}")
                else:
                    filename = "markdown_text.md"
                    logger.info(f"Using default filename: {filename}")
                
                if content:
                    logger.info(f"Content validation passed. Processing {len(content)} characters")
                    logger.info(f"Content preview: {content[:200]}..." if len(content) > 200 else f"Full content: {content}")
                    st.write(f"🔍 **Debug:** Starting conversion of {len(content)} characters")
                    
                    # Store original content for comparison
                    original_content = content
                    
                    if use_openai and api_key:
                        logger.info("AI optimization path selected")
                        logger.info(f"API key available: {bool(api_key)}")
                        logger.info(f"use_openai flag: {use_openai}")
                        
                        # Check if we've already optimized this content
                        content_hash = str(hash(content[:200]))  # Use first 200 chars for hash
                        optimization_key = f"optimization_complete_{content_hash}"
                        optimized_content_key = f"optimized_content_{content_hash}"  # Define this key here for both paths
                        already_optimized = st.session_state.get(optimization_key, False)
                        
                        logger.info(f"Content hash: {content_hash}")
                        logger.info(f"Optimization key: {optimization_key}")
                        logger.info(f"Optimized content key: {optimized_content_key}")
                        logger.info(f"Already optimized: {already_optimized}")
                        
                        if already_optimized:
                            logger.info("Content already optimized, retrieving from session state...")
                            # Retrieve optimized content from session state
                            content = st.session_state.get(optimized_content_key, content)
                            logger.info(f"Retrieved optimized content length: {len(content)}")
                        else:
                            logger.info("Running AI optimization for the first time...")
                            # Store original content
                            original_content = content
                            
                            # Only run optimization if we haven't already done it
                            logger.info("AI optimization enabled - starting optimization process")
                            st.subheader("🤖 AI Optimization")
                            st.write("🔍 **Debug:** AI optimization enabled, starting process...")
                            
                            # Show optimization progress
                            optimization_progress = st.progress(0)
                            optimization_status = st.empty()
                            
                            def update_optimization_progress(status, progress):
                                optimization_status.text(status)
                                optimization_progress.progress(progress)
                            
                            # Perform optimization
                            with st.spinner("Optimizing content for speech using GPT-4o..."):
                                content = optimize_for_speech(content, api_key, update_optimization_progress)
                            
                            st.success("✅ Content optimized for speech!")
                            
                            # Store optimized content in session state
                            st.session_state[optimization_key] = True
                            st.session_state[optimized_content_key] = content
                            st.session_state[f"original_content_{content_hash}"] = original_content
                            logger.info(f"Stored optimized content in session state with key: {optimized_content_key}")
                        
                        # Show comparison of original vs optimized content (always show this)
                        st.subheader("📝 Content Comparison")
                        
                        # Get original content for comparison
                        original_content_for_display = original_content if not already_optimized else st.session_state.get(f"original_content_{content_hash}", content)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Original Content:**")
                            st.text_area("Original", value=original_content_for_display[:1000] + "..." if len(original_content_for_display) > 1000 else original_content_for_display, height=200, disabled=True, key="original_preview")
                        
                        with col2:
                            st.markdown("**Optimized Content:**")
                            st.text_area("Optimized", value=content[:1000] + "..." if len(content) > 1000 else content, height=200, disabled=True, key="optimized_preview")
                        
                        # Show full optimized content in an expander
                        with st.expander("📖 View Full Optimized Content"):
                            st.text_area("Complete Optimized Content", value=content, height=400, disabled=True, key="full_optimized")
                        
                        # Ask user if they want to proceed
                        st.info("📋 Review the optimized content above. Click 'Proceed with Conversion' to continue or edit the content manually below.")
                        
                        # Allow manual editing of optimized content
                        content = st.text_area(
                            "Edit Optimized Content (Optional):",
                            value=content,
                            height=200,
                            help="You can make manual adjustments to the optimized content before conversion",
                            key="manual_edit"
                        )
                        
                        # Debug info
                        if content:
                            st.info(f"📊 Content ready for conversion: {len(content)} characters")
                        else:
                            st.error("⚠️ Content is empty! Please check the optimized content above.")
                        
                        # Proceed button - use a stable content hash for the button key
                        content_hash = hashlib.md5(content.encode()).hexdigest()[:8] 
                        proceed_key = f"proceed_conversion_{content_hash}"
                        
                        logger.info(f"About to show proceed button with key: {proceed_key}")
                        logger.info(f"Content hash: {content_hash}")
                        
                        # Create the button and check if it was clicked
                        proceed_button_clicked = st.button("🎵 Proceed with Conversion", type="secondary", use_container_width=True, key=proceed_key)
                        logger.info(f"Proceed button returned: {proceed_button_clicked}")
                        
                        if proceed_button_clicked:
                            logger.info("=== PROCEED BUTTON CLICKED ===")
                            logger.info(f"Proceed button clicked! Content length: {len(content) if content else 0}")
                            
                            if not content or not content.strip():
                                st.error("❌ Cannot proceed: Content is empty!")
                                logger.error("Conversion failed: Content is empty")
                            else:
                                logger.info("Setting session state for conversion...")
                                st.session_state.should_convert = True
                                st.session_state.conversion_content = content
                                st.session_state.conversion_filename = filename
                                logger.info(f"Session state set:")
                                logger.info(f"- should_convert: {st.session_state.should_convert}")
                                logger.info(f"- conversion_content length: {len(st.session_state.conversion_content)}")
                                logger.info(f"- conversion_filename: {st.session_state.conversion_filename}")
                                logger.info("About to call st.rerun()...")
                                st.rerun()
                        else:
                            logger.info("Proceed button was NOT clicked this run")
                        
                        # Stop execution to show the review UI
                        st.info("👆 Review the content above, then click 'Proceed with Conversion' to continue.")
                        logger.info("Waiting for user to click proceed button - stopping execution")
                        st.stop()  # Stop execution until user is ready to proceed
                    else:
                        logger.info("Direct conversion path selected (no AI optimization)")
                        # No OpenAI optimization, proceed directly to conversion
                        logger.info("No AI optimization - storing content for conversion")
                        logger.info("Setting session state for direct conversion...")
                        st.session_state.should_convert = True
                        st.session_state.conversion_content = content
                        st.session_state.conversion_filename = filename
                        logger.info(f"Session state set for direct conversion:")
                        logger.info(f"- should_convert: {st.session_state.should_convert}")
                        logger.info(f"- conversion_content length: {len(st.session_state.conversion_content)}")
                        logger.info(f"- conversion_filename: {st.session_state.conversion_filename}")
                        logger.info("About to call st.rerun() for direct conversion...")
                        st.rerun()
                else:
                    logger.warning("No content provided for conversion")
                    st.warning("⚠️ Please upload a file or paste some markdown content to convert.")

    logger.info("=== MAIN FUNCTION ENDING (NORMAL PATH) ===")

if __name__ == "__main__":
    main()
