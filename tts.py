import markdown
from gtts import gTTS
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from bs4 import BeautifulSoup
import threading

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
    # Remove unwanted Markdown elements by replacing them with appropriate text or removing them
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

def markdown_to_speech(md_file, output_file, lang, progress_var, chunk_size, signs_to_exclude):
    try:
        # Read the markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Convert markdown to HTML
        html_text = markdown.markdown(md_text)
        
        # Convert HTML to plain text
        soup = BeautifulSoup(html_text, "html.parser")
        plain_text = ''.join(soup.find_all(string=True))
        
        # Clean the extracted text
        cleaned_text = clean_text(plain_text, signs_to_exclude)

        # Split text into chunks to handle gTTS limits
        text_chunks = [cleaned_text[i:i + chunk_size] for i in range(0, len(cleaned_text), chunk_size)]
        
        # Initialize progress
        total_chunks = len(text_chunks)
        progress_step = 100 / total_chunks
        
        # Convert each chunk to speech and save as a temporary file
        temp_files = []
        for i, chunk in enumerate(text_chunks):
            tts = gTTS(chunk, lang=lang)
            temp_file = f"{output_file}_part_{i}.mp3"
            tts.save(temp_file)
            temp_files.append(temp_file)
            
            # Update progress bar
            progress_var.set((i + 1) * progress_step)
        
        # Combine all temporary files into a single output file
        combine_audio_chunks(temp_files, output_file)
        
        # Clean up temporary files
        for temp_file in temp_files:
            os.remove(temp_file)
        
        # Update progress bar to 100%
        progress_var.set(100)
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")

def combine_audio_chunks(temp_files, output_file):
    try:
        # Combine MP3 files using ffmpeg
        file_list = '|'.join(temp_files)
        command = f'ffmpeg -i "concat:{file_list}" -acodec copy "{output_file}"'
        os.system(command)
    except Exception as e:
        print(f"Error during concatenation: {e}")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def convert_to_speech():
    markdown_file = entry.get()
    selected_language = lang_combobox.get()
    chunk_size = chunk_size_var.get()
    if markdown_file and selected_language:
        output_audio_file = os.path.splitext(markdown_file)[0] + ".mp3"
        lang_code = LANGUAGES[selected_language]
        progress_var.set(0)
        status_label.config(text="Converting...")
        
        # Get selected signs to exclude
        signs_to_exclude = [SIGNS[sign_text] for sign_text, var in sign_vars.items() if var.get() == 1]
        
        # Start conversion in a separate thread
        t = threading.Thread(target=markdown_to_speech, args=(markdown_file, output_audio_file, lang_code, progress_var, chunk_size, signs_to_exclude))
        t.start()
        
        # Check the thread periodically and update GUI when it's finished
        root.after(100, check_thread, t, output_audio_file)
    else:
        status_label.config(text="Please select a Markdown file and language.")

def check_thread(thread, output_audio_file):
    if thread.is_alive():
        root.after(100, check_thread, thread, output_audio_file)
    else:
        status_label.config(text="Conversion complete. Audio saved as " + output_audio_file)
        progress_var.set(100)

# Create main window
root = tk.Tk()
root.title("Markdown to Speech Converter")

# Create frame
frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky="nsew")

# Create widgets
label = ttk.Label(frame, text="Select a Markdown file:")
label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

entry = ttk.Entry(frame, width=50)
entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

browse_button = ttk.Button(frame, text="Browse", command=browse_file)
browse_button.grid(row=1, column=1, padx=5, pady=5)

lang_label = ttk.Label(frame, text="Select a language:")
lang_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

lang_combobox = ttk.Combobox(frame, values=list(LANGUAGES.keys()), state="readonly")
lang_combobox.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
lang_combobox.current(0)  # Set default language to English

chunk_size_label = ttk.Label(frame, text="Chunk size:")
chunk_size_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

chunk_size_var = tk.IntVar(value=1000)
chunk_size_slider = ttk.Scale(frame, from_=500, to_=5000, orient="horizontal", variable=chunk_size_var)
chunk_size_slider.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

chunk_size_display = ttk.Label(frame, textvariable=chunk_size_var)
chunk_size_display.grid(row=5, column=1, padx=5, pady=5, sticky="w")

signs_label = ttk.Label(frame, text="Exclude these signs:")
signs_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")

sign_vars = {}
for i, (sign_text, sign) in enumerate(SIGNS.items()):
    var = tk.IntVar()
    checkbutton = ttk.Checkbutton(frame, text=sign_text, variable=var)
    checkbutton.grid(row=7+i, column=0, padx=5, pady=5, sticky="w")
    sign_vars[sign_text] = var

convert_button = ttk.Button(frame, text="Convert to Speech", command=convert_to_speech)
convert_button.grid(row=7+len(SIGNS), column=0, columnspan=2, padx=5, pady=5, sticky="ew")

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.grid(row=8+len(SIGNS), column=0, columnspan=2, padx=5, pady=5, sticky="ew")

status_label = ttk.Label(frame, text="")
status_label.grid(row=9+len(SIGNS), column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Configure grid
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)
frame.rowconfigure(2, weight=1)
frame.rowconfigure(3, weight=1)
frame.rowconfigure(4, weight=1)
frame.rowconfigure(5, weight=1)
for i in range(6, 10+len(SIGNS)):
    frame.rowconfigure(i, weight=1)

# Run GUI
root.mainloop()