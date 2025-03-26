import tkinter as tk
from tkinter import scrolledtext, ttk, font
import edge_tts
import asyncio
import os
import random
import threading
import time
import pygame
from pygame import mixer
from mutagen.mp3 import MP3
from gtts import gTTS
import re


class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Application")
        self.root.geometry("600x650")
        
        # Calculate position (10px from right, 10px from top)
        screen_width = self.root.winfo_screenwidth()
        window_width = 600  # Match your window width
        x_position = screen_width - window_width - 20  # 10px from right edge
        y_position = 20  # 10px from top
        
        # Set position
        self.root.geometry(f"+{x_position}+{y_position}")
        
        self.root.resizable(True, True)
        
        self.background_music = None
        self.play_background_music = tk.BooleanVar(value=False)
        
        self.directory_name = os.path.dirname(os.path.abspath(__file__))
        
        # Define custom fonts
        self.custom_font = ("Ubuntu", 8, "bold")
        self.small_font = ("Ubuntu", 8, "bold")
        self.textarea_font = ("Consolas", 12, "bold")
        
        # Set dark theme colors
        self.dark_bg = "#1e1e1e"
        self.dark_secondary_bg = "#2d2d2d"
        self.gray_color = "#adacac"
        self.dark_text = "#e0e0e0"
        self.accent_color = "#d1cfcf"  
        self.error_color = "#ff5555"   
        
        # Apply dark theme to root window
        self.root.configure(bg=self.dark_bg)
        
        # Set up ttk styles for dark theme
        self.setup_styles()
        
        # Initialize pygame mixer for audio playback
        # Initialize pygame mixer for audio playback
        mixer.init()
        mixer.music.set_volume(0.7)  # Set default volume to 70%
        
        # Current audio file path
        self.current_audio_file = None
        self.is_playing = False
        self.audio_length = 0
        self.audio_pos = 0
        
        # Track pause positions
        self.paused_pos = 0
        self.start_time = 0
        
        # Auto-generate flag
        self.auto_generate = tk.BooleanVar(value=False)
        
        # Speech rate
        self.speech_rate = tk.IntVar(value=40)  # Default to medium rate
        
        # Text modification tracking
        self.last_text = ""
        self.text_modified_timer = None
        
        # Text area font size
        self.text_font_size = 12  # Default font size
        
        # Edge TTS voices - Using predefined list of voices
        self.voices = {
            # United States (English)
            "US Male (Andrew)": "en-US-AndrewNeural",
            "UK Female (Sonia)": "en-GB-SoniaNeural",
            "UK Female (Mia)": "en-GB-MiaNeural",
            "UK Male (Ryan)": "en-GB-RyanNeural",
            "New Zealand Female (Molly)": "en-NZ-MollyNeural",
            
            "US Female (Jenny)": "en-US-JennyNeural",
            "US Female (Aria)": "en-US-AriaNeural",
            "US Female (Ana)": "en-US-AnaNeural",
            "US Female (Michelle)": "en-US-MichelleNeural",
            "US Female (Sara)": "en-US-SaraNeural",
            "US Male (Guy)": "en-US-GuyNeural",
            "US Male (Davis)": "en-US-DavisNeural",
            "US Male (Jason)": "en-US-JasonNeural",
            "US Male (Tony)": "en-US-TonyNeural",
            
            
            # United Kingdom (English)
            
            "UK Female (Libby)": "en-GB-LibbyNeural",
            
            "UK Female (Abbie)": "en-GB-AbbieNeural",
            
            "UK Male (Thomas)": "en-GB-ThomasNeural",
            
            # Australia (English)
            "Australian Female (Natasha)": "en-AU-NatashaNeural",
            "Australian Female (Isla)": "en-AU-IslaNeural",
            "Australian Male (William)": "en-AU-WilliamNeural",
            "Australian Male (Liam)": "en-AU-LiamNeural",
            
            "French Female (Denise)": "fr-FR-DeniseNeural",
            "French Male (Henri)": "fr-FR-HenriNeural",
            
            "Arabic Female (Hoda)": "ar-EG-HodaNeural",
            "Arabic Male (Hamed)": "ar-EG-HamedNeural",
            
            "German Female (Katja)": "de-DE-KatjaNeural",
            "German Male (Conrad)": "de-DE-ConradNeural",
            
            
            "New Zealand Male (Mitchell)": "en-NZ-MitchellNeural",
            
            # Spanish
            "Spanish Female (Elvira)": "es-ES-ElviraNeural",
            "Spanish Male (Alvaro)": "es-ES-AlvaroNeural",
            
            # Google TTS Voices
            "Google American Female": ("en", "com"),
            "Google British Female": ("en", "co.uk"),
            "Google Australian Female": ("en", "com.au"),
            "Google Indian Female": ("en", "co.in"),
            "Google French Female": ("fr", "fr"),
            "Google German Male": ("de", "de"),
            "Google Spanish Male": ("es", "es"),
            "Google Italian Male": ("it", "it"),
        }
        
        # Create UI elements
        self.create_widgets()
        self.create_menu()
        
        # Bind Ctrl+MouseWheel event
        self.text_area.bind("<Control-MouseWheel>", self.on_ctrl_scroll)
    
    def setup_styles(self):
        """Set up ttk styles for dark theme"""
        style = ttk.Style()
    
        # Set the theme to clam for better styling control
        style.theme_use("clam")
        
        # Create and configure named fonts
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Ubuntu", size=12)
        
        
        
        # Configure frame styles
        style.configure("TFrame", background=self.dark_bg)
        style.configure("TLabelframe", background=self.dark_bg, foreground=self.dark_text,font=self.custom_font)
        style.configure("TLabelframe.Label", background=self.dark_bg, foreground=self.dark_text,font=self.custom_font)
        
        # Configure label styles
        style.configure("TLabel", background=self.dark_bg, foreground=self.dark_text,font=self.custom_font)
        
        # Configure button styles - with black foreground color
        style.configure("TButton", 
                       background=self.gray_color, 
                       foreground="black",
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor=self.accent_color,
                       font=self.custom_font)
        
        # Button hover and pressed states
        style.map("TButton", 
                 background=[("active", self.accent_color), 
                            ("pressed", self.accent_color)], 
                 foreground=[("active", "black"),
                            ("pressed", "black")])
        
        # Configure checkbox styles
        style.configure("TCheckbutton", 
                       background=self.dark_bg, 
                       foreground=self.dark_text,
                       font=self.small_font)
        style.map("TCheckbutton",
                 background=[("active", self.dark_bg)],
                 foreground=[("active", self.dark_text)])
        
        # Configure scale (slider) style
        style.configure("TScale", 
                       background=self.dark_bg, 
                       troughcolor=self.dark_secondary_bg)
        
        # Configure combobox style - with black foreground color
        style.configure("TCombobox", 
                       fieldbackground=self.dark_secondary_bg,
                       background=self.dark_secondary_bg,
                       foreground="black",
                       selectbackground=self.accent_color,
                       selectforeground="black",
                       font=self.small_font)
        
        style.map("TCombobox",
                  fieldbackground=[("readonly", self.accent_color)],
                  background=[("readonly", self.accent_color)],
                  foreground=[("readonly", "black")],
                  selectbackground=[("readonly", self.accent_color)],
                  selectforeground=[("readonly", "black")])
        
        # Set dropdown list colors (this requires tk option settings)
        self.root.option_add('*TCombobox*Listbox.background', self.gray_color)
        self.root.option_add('*TCombobox*Listbox.foreground', "black")
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.accent_color)
        self.root.option_add('*TCombobox*Listbox.selectForeground', "black")
        self.root.option_add('*TCombobox*Listbox.font', self.small_font)
        
        # Configure progress bar style
        style.configure("TProgressbar", 
                       background=self.accent_color,
                       troughcolor=self.dark_secondary_bg)
        
        # Small button style
        style.configure('Small.TButton', padding=(2, 0))
    
    
    
    def on_ctrl_scroll(self, event):
        """Handle Ctrl+MouseWheel to change font size"""
        if event.delta > 0:  # Scroll up - increase font size
            self.text_font_size = min(36, self.text_font_size + 1)  # Cap at 36
        else:  # Scroll down - decrease font size
            self.text_font_size = max(8, self.text_font_size - 1)  # Minimum 8
        
        # Update the font
        self.text_area.configure(font=("Consolas", self.text_font_size))
        
        # Update status
        self.status_var.set(f"Font size: {self.text_font_size}pt")
        self.reset_status_color()
    
    
    
    
    
    def create_menu(self):
        """Create the menu bar with File menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        
        
        # Options menu
        options_menu = tk.Menu(menubar, tearoff=0)
                              #bg=self.dark_secondary_bg,
                              #fg=self.dark_text,
                              #activebackground=self.accent_color,
                              #activeforeground="black")
        options_menu.add_checkbutton(label="Play Background Music", 
                                    variable=self.play_background_music,
                                    command=self.toggle_background_music)
        menubar.add_cascade(label="Options", menu=options_menu)
        
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        ButtonXPadding = 4
        ButtonYPadding = 1
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Voice selection and rate control
        settings_frame = ttk.LabelFrame(main_frame, text="Voice Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=ButtonYPadding)
        
        # Voice dropdown with navigation buttons
        voice_frame = ttk.Frame(settings_frame)
        voice_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(voice_frame, text="Select Voice:").pack(side=tk.LEFT, padx=ButtonXPadding)
        
        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly", width=30)
        # Set the dropdown values to the human-readable voice names
        self.voice_dropdown['values'] = list(self.voices.keys())
        # Set default voice
        if self.voice_dropdown['values']:
            self.voice_dropdown.current(0)
        self.voice_dropdown.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Add up and down buttons for voice navigation
        nav_buttons_frame = ttk.Frame(voice_frame)
        nav_buttons_frame.pack(side=tk.LEFT, padx=2)
        
        up_button = ttk.Button(nav_buttons_frame, text="▲", width=2, command=self.navigate_voice_up, cursor='hand2', style='Small.TButton')
        up_button.pack(side=tk.TOP, pady=1)
        
        down_button = ttk.Button(nav_buttons_frame, text="▼", width=2, command=self.navigate_voice_down, cursor='hand2', style='Small.TButton')
        down_button.pack(side=tk.BOTTOM, pady=1)
        
        # Speech rate control
        rate_frame = ttk.Frame(settings_frame)
        rate_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(rate_frame, text="Speech Rate:").pack(side=tk.LEFT, padx=ButtonXPadding)
        
        def on_slider_change(value):
            # Round to nearest multiple of 5
            rounded_value = round(float(value) / 5) * 5
            # Set the variable to the rounded value
            self.speech_rate.set(rounded_value)
            
        
        # Rate slider
        rate_slider = ttk.Scale(rate_frame, 
                               from_=0, 
                               to=100, 
                               orient=tk.HORIZONTAL, 
                               variable=self.speech_rate, 
                               length=200,
                               cursor='hand2',
                               command=on_slider_change)
        rate_slider.pack(side=tk.LEFT, padx=ButtonXPadding, fill=tk.X, expand=True)
        
        # Rate value display
        self.rate_display = ttk.Label(rate_frame, width=5)
        self.rate_display.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Update rate display function
        def update_rate_display(*args):
            val = self.speech_rate.get()
            self.rate_display.config(text=f"{val}%")
                
        # Call initially and bind to variable changes
        update_rate_display()
        self.speech_rate.trace_add("write", update_rate_display)
        
        # Text input area with controls
        text_frame = ttk.LabelFrame(main_frame, text="Enter Text", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=ButtonYPadding)
        
        # Controls above text area
        text_controls_frame = ttk.Frame(text_frame)
        text_controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Clear button
        clear_button = ttk.Button(text_controls_frame, text="Clear Text", command=self.clear_text, cursor='hand2', style='Small.TButton')
        clear_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Paste button - NEW
        paste_button = ttk.Button(text_controls_frame, text="Paste", command=self.paste_text, cursor='hand2', style='Small.TButton')
        paste_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Clear Unicode button - NEW
        clear_unicode_button = ttk.Button(text_controls_frame, text="Clear Unicode", command=self.clear_unicode, cursor='hand2', style='Small.TButton')
        clear_unicode_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Markdown to Text button - NEW
        markdown_button = ttk.Button(text_controls_frame, text="Markdown to Text", command=self.clear_markdown, cursor='hand2', style='Small.TButton')
        markdown_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Auto-generate checkbox
        auto_generate_check = ttk.Checkbutton(
            text_controls_frame, 
            text="Auto-generate on text change", 
            variable=self.auto_generate,
            cursor='hand2',
            command=self.toggle_auto_generate
        )
        auto_generate_check.pack(side=tk.RIGHT, padx=ButtonXPadding)
        
        # Text area with dark theme colors
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            width=40, 
            height=10,
            bg=self.dark_secondary_bg,
            fg=self.dark_text,
            insertbackground=self.dark_text,  # Cursor color
            selectbackground=self.accent_color,
            selectforeground="black",  # Changed from self.dark_text to "black"
            font=self.textarea_font
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=ButtonXPadding, pady=ButtonYPadding)
        self.text_area.pack_propagate(False) 
        
        # Configure scrollbar colors
        self.text_area.config(highlightbackground=self.dark_secondary_bg, 
                             highlightcolor=self.accent_color)
        
        # Bind text changes
        self.text_area.bind("<KeyRelease>", self.on_text_change)
        
        # Generate button
        generate_button = ttk.Button(main_frame, text="Generate Speech", command=self.generate_speech, cursor='hand2', style='Small.TButton')
        generate_button.pack(pady=10)
        
        # Audio player frame
        player_frame = ttk.LabelFrame(main_frame, text="Audio Player", padding="5")
        player_frame.pack(fill=tk.X, pady=ButtonYPadding)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(player_frame, orient="horizontal", length=300, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, padx=ButtonXPadding, pady=ButtonYPadding)
        
        self.progress_bar.bind("<Button-1>", self.progress_bar_click)
        
        # Time display
        time_frame = ttk.Frame(player_frame)
        time_frame.pack(fill=tk.X, padx=ButtonXPadding)
        
        self.current_time = ttk.Label(time_frame, text="0:00")
        self.current_time.pack(side=tk.LEFT)
        
        self.total_time = ttk.Label(time_frame, text="/ 0:00")
        self.total_time.pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = ttk.Frame(player_frame)
        control_frame.pack(pady=ButtonYPadding)

        # Volume down button
        vol_down_button = ttk.Button(control_frame, text="-", command=self.decrease_volume, 
                                   width=3, cursor='hand2', style='Small.TButton')
        vol_down_button.pack(side=tk.LEFT, padx=ButtonXPadding)

        # Play button
        self.play_button = ttk.Button(control_frame, text="Play", command=self.toggle_play, 
                                    state=tk.DISABLED, cursor='hand2', style='Small.TButton')
        self.play_button.pack(side=tk.LEFT, padx=ButtonXPadding)

        # Stop button
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_audio, 
                                    state=tk.DISABLED, cursor='hand2', style='Small.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=ButtonXPadding)

        # Volume up button
        vol_up_button = ttk.Button(control_frame, text="+", command=self.increase_volume, 
                                 width=3, cursor='hand2', style='Small.TButton')
        vol_up_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Status label - changed to regular tk.Label to allow color changes
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Select a voice and enter text.")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, bg=self.dark_bg, fg=self.dark_text)
        self.status_label.pack(pady=ButtonYPadding)
    
    
    
    
    def increase_volume(self):
        """Increase the volume by 10%"""
        current_vol = mixer.music.get_volume()
        new_vol = min(2.0, current_vol + 0.1)  # Cap at 1.0 (max volume)
        mixer.music.set_volume(new_vol)
        self.status_var.set(f"Volume: {int(new_vol * 100)}%")
        self.reset_status_color()

    def decrease_volume(self):
        """Decrease the volume by 10%"""
        current_vol = mixer.music.get_volume()
        new_vol = max(0.0, current_vol - 0.1)  # Minimum is 0.0 (silent)
        mixer.music.set_volume(new_vol)
        self.status_var.set(f"Volume: {int(new_vol * 100)}%")
        self.reset_status_color()
    
    
    def progress_bar_click(self, event):
        """Handle click on progress bar to seek to a specific position"""
        if not self.current_audio_file or self.audio_length <= 0:
            return
            
        # Calculate the relative position of the click
        progress_width = self.progress_bar.winfo_width()
        click_position = event.x / progress_width
        
        # Calculate the target time in seconds
        target_seconds = click_position * self.audio_length
        
        # Update the progress bar
        progress = (target_seconds / self.audio_length) * 100
        self.progress_var.set(progress)
        
        # Update time display
        mins, secs = divmod(int(target_seconds), 60)
        self.current_time.configure(text=f"{mins}:{secs:02d}")
        
        # Seek to the new position
        self.seek_to_position(target_seconds)

    def seek_to_position(self, target_seconds):
        """Seek to a specific position in the audio using pydub to slice the audio file"""
        if not self.current_audio_file:
            return
        
        was_playing = self.is_playing
        
        # Stop current playback
        if self.is_playing:
            mixer.music.stop()
            self.is_playing = False
        
        try:
            # For pygame's mixer, we need to convert target_seconds to milliseconds
            # Load the audio file
            mixer.music.load(self.current_audio_file)
            
            # Set the start time to account for seeking
            self.start_time = time.time() - target_seconds
            self.paused_pos = target_seconds
            
            # Resume playing if it was playing before
            if was_playing:
                # Try to play from position - this works in some pygame versions and formats
                try:
                    mixer.music.play(start=target_seconds)
                    self.is_playing = True
                    self.play_button.configure(text="Pause")
                    
                    # Restart progress updates
                    self.update_progress()
                except:
                    # Fallback: play from beginning but adjust our tracking variables
                    mixer.music.play()
                    self.is_playing = True
                    self.play_button.configure(text="Pause")
                    
                    # Restart progress updates
                    self.update_progress()
            
        except Exception as e:
            self.display_error(f"Error seeking: {str(e)}")
            print(f"Error seeking: {str(e)}")
    
    
    
    
    
    def paste_text(self):
        """Paste text from clipboard into the text area"""
        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()
            
            # Insert at current cursor position or at the end if no selection
            if self.text_area.tag_ranges("sel"):
                # Replace selected text
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert("insert", clipboard_text)
            else:
                # Just insert at current position
                self.text_area.insert("insert", clipboard_text)
                
            # Update status
            self.status_var.set("Text pasted from clipboard")
            self.reset_status_color()
            
            # Update last text to track changes
            self.last_text = self.text_area.get("1.0", tk.END).strip()
            
            # Auto-generate if enabled
            if self.auto_generate.get() and clipboard_text.strip():
                # Set a small delay before generating
                self.text_modified_timer = self.root.after(500, self.generate_speech)
                
        except tk.TclError:
            # Error when clipboard is empty or contains non-text data
            self.display_error("No text available in clipboard")
    
    
    def clear_markdown(self):
        """Remove markdown formatting characters from the text while preserving newlines and handling code blocks properly"""
        # Get current text
        current_text = self.text_area.get("1.0", tk.END)
        
        # Process text line by line to better preserve newlines
        lines = current_text.splitlines(True)  # Keep the newlines
        cleaned_lines = []
        
        in_code_block = False
        
        for line in lines:
            # Check for code block start with language identifier
            code_block_match = re.match(r'^\s*```([a-zA-Z0-9_]*)\s*$', line)
            if code_block_match:
                if in_code_block:
                    # End of code block - add marker but no content
                    cleaned_lines.append('```\n')
                else:
                    # Start of code block - add marker without language identifier
                    cleaned_lines.append('```\n')
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                # Skip all content within code blocks
                continue
            
            # Rest of the function remains the same as in the original implementation
            # Remove parentheses and their content
            line = re.sub(r'\([^)]*\)', '', line)
            
            # Remove markdown headers (### Header) and add newline
            if re.match(r'^\s*#{1,6}\s+', line):
                cleaned_line = re.sub(r'^\s*#{1,6}\s+', '', line)
                cleaned_line += '\n'
                cleaned_lines.append(cleaned_line)
                continue
                
            # Handle lines starting with numbers or hyphens
            if re.match(r'^\s*\d+\.\s+', line) or re.match(r'^\s*-\s+', line):
                cleaned_line = re.sub(r'^\s*\d+\.\s+', '', line)  # Remove numbered list
                cleaned_line = re.sub(r'^\s*-\s+', '', cleaned_line)  # Remove bullet point
                cleaned_line += '\n'
                cleaned_lines.append(cleaned_line)
                continue
            
            # Remove emphasis markers
            cleaned_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Bold
            cleaned_line = re.sub(r'\*([^*]+)\*', r'\1', cleaned_line)  # Italic
            cleaned_line = re.sub(r'__([^_]+)__', r'\1', cleaned_line)  # Bold
            cleaned_line = re.sub(r'_([^_]+)_', r'\1', cleaned_line)  # Italic
            
            # Remove inline code
            cleaned_line = re.sub(r'`([^`]+)`', r'\1', cleaned_line)
            
            # Remove blockquotes
            cleaned_line = re.sub(r'^\s*>\s+', '', cleaned_line)
            
            # Remove horizontal rules
            if re.match(r'^\s*[-*_]{3,}\s*$', cleaned_line):
                cleaned_line = ''
            
            # Remove link syntax (keeping link text)
            cleaned_line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned_line)
            
            # Remove image syntax
            cleaned_line = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', cleaned_line)
            
            cleaned_lines.append(cleaned_line)
        
        # Join all lines back together
        cleaned_text = ''.join(cleaned_lines)
        
        # Final cleanup
        cleaned_text = cleaned_text.replace('**', '')
        cleaned_text = cleaned_text.replace('*', '')
        cleaned_text = cleaned_text.replace('`', '')
        
        # Clear and insert cleaned text
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", cleaned_text)
        
        # Update status
        self.status_var.set("Markdown formatting removed")
        self.reset_status_color()
        
        # Update last text to prevent auto-generation if enabled
        self.last_text = cleaned_text
    
    
    
    
    def clear_unicode(self):
        """Clear Unicode emojis from the text area"""
        # Get current text
        current_text = self.text_area.get("1.0", tk.END)
        
        
        current_text = current_text.replace('e.g.', ' \n for example ')
        current_text = current_text.replace('i.e.', ' \n in other words ')
        current_text = current_text.replace('(', '\n')
        current_text = current_text.replace(')', '')
        current_text = current_text.replace('{', '')
        current_text = current_text.replace('}', '')
        current_text = current_text.replace('$', '')
        current_text = current_text.replace('@', '')
        current_text = current_text.replace('&', '')
        
        
        
        # Use a regex to remove emojis and other unicode characters
        # This pattern matches emojis and other special unicode characters
        emoji_pattern = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0000254E"  # enclosed characters
            "\U0000FE0F"             # VS16
            "\U0000200D"             # Zero Width Joiner
            "\U0000203C-\U00002049"  # Exclamation and Question Marks
            "\U000020D0-\U0000214F"  # Combining marks and letterlike symbols
            "\U00002190-\U00002199"  # Arrows
            "\U000021A9-\U000021AA"  # Arrows with hook
            "\U00002300-\U000023FF"  # Miscellaneous Technical
            "\U00002500-\U000025FF"  # Box Drawing and Geometric Shapes
            "\U00002600-\U000026FF"  # Miscellaneous Symbols
            "\U0000270C-\U0000270D"  # Victory Hand
            "⏰⏱⏲⏳✅❌❓❗"          # Common special emojis
            "⌚⌛⏩⏪⏫⏬⏭⏮⏯⭐"        # More common special emojis
            "〰〽"                    # Wavy dash and part alternation mark
            "]+", flags=re.UNICODE)
        
        # Replace emojis with empty string
        cleaned_text = emoji_pattern.sub(r'', current_text)
        
        # Remove all https:// URLs
        #url_pattern = re.compile(r'https?://\S+')
        #cleaned_text = url_pattern.sub(r'', cleaned_text)
        
        # Improved URL cleaning - removes https:// but keeps domain
        url_pattern = re.compile(r'https://([^\s/]+)')
        cleaned_text = url_pattern.sub(r'https \1', cleaned_text)  # Replace with just the domain
        
        url_pattern = re.compile(r'http://([^\s/]+)')
        cleaned_text = url_pattern.sub(r'http \1', cleaned_text)  # Replace with just the domain
        
        # Remove all file:// URLs completely
        file_url_pattern = re.compile(r'file://([^\s/]+)')
        cleaned_text = file_url_pattern.sub(r'file \1', cleaned_text)
        
        
        """
        acronyms = {
            'CSRF': 'C S R F',
            'SQL': 'S Q L',
            'XSS': 'X S S',
            'XXE': 'X X E',
            'SSRF': 'S S R F',
            'RCE': 'R C E',
            'LFI': 'L F I',
            'RFI': 'R F I'
        }
        
        # Create a regex pattern that matches these acronyms as whole words
        acronym_pattern = re.compile(r'\b(' + '|'.join(re.escape(acronym) for acronym in acronyms.keys()) + r')\b')
        
        # Replace each acronym with its spaced-out version
        cleaned_text = acronym_pattern.sub(lambda match: acronyms[match.group(0)], cleaned_text)
        """
        
        
        # Define the words to split (case-insensitive)
        words_to_split = [
            "SQL", 
            "DOM", 
            "CSRF", 
            "XSRF", 
            "XSS", 
            "XXE", 
            "SSRF", 
            "RCE", 
            "LFI", 
            "RFI" , 
            "CSP" , 
            "SOP" , 
            "CSPT" , 
            "CVE" , 
            "CWE" , 
            "CSV" , 
            "HTTP",
            "HTTPS",
            "/etc/",
            "DoS"
        ]
        
        # Build a regex pattern to match these words as whole words
        split_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, words_to_split)) + r')\b',
            flags=re.IGNORECASE
        )
        
        # Replace matched words with spaced letters (e.g., "CSRF" → "C S R F")
        def split_word(match):
            return ' '.join(list(match.group(0).upper()))  # Ensure uppercase
        
        cleaned_text = split_pattern.sub(split_word, cleaned_text)
        
        
        
        
        # NEW: Replace dots ONLY if not followed by space or at end of sentence
        cleaned_text = re.sub(
            r'\.(?!\s|$)',  # Dot NOT followed by space or end of line
            ' dot ',
            cleaned_text
        )
        
        
        cleaned_text = re.sub(
            r'--',  # Dot NOT followed by space or end of line
            ' dash dash ',
            cleaned_text
        )
        
        # Remove forward slashes (unchanged)
        #cleaned_text = cleaned_text.replace('/', '')
        
        
        # Remove all forward slashes
        #cleaned_text = cleaned_text.replace('/', '')
        
        # Clear and insert cleaned text
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", cleaned_text)
        
        
        
        # Update status
        self.status_var.set("Unicode emojis removed")
        self.reset_status_color()
        
        
        # Update last text to prevent auto-generation if enabled
        self.last_text = cleaned_text
    
    
    
    def navigate_voice_up(self):
        """Navigate to the previous voice in the dropdown"""
        values = self.voice_dropdown['values']
        if not values:
            return
            
        current_idx = self.voice_dropdown.current()
        if current_idx > 0:
            self.voice_dropdown.current(current_idx - 1)
            # Update status with new selection
            self.status_var.set(f"Selected voice: {self.voice_var.get()}")
            self.reset_status_color()
    
    def navigate_voice_down(self):
        """Navigate to the next voice in the dropdown"""
        values = self.voice_dropdown['values']
        if not values:
            return
            
        current_idx = self.voice_dropdown.current()
        if current_idx < len(values) - 1:
            self.voice_dropdown.current(current_idx + 1)
            # Update status with new selection
            self.status_var.set(f"Selected voice: {self.voice_var.get()}")
            self.reset_status_color()
    
    def clear_text(self):
        """Clear the text area"""
        self.text_area.delete("1.0", tk.END)
        self.last_text = ""
    
    def toggle_auto_generate(self):
        """Handle auto-generate checkbox toggle"""
        if self.auto_generate.get():
            self.status_var.set("Auto-generate enabled")
        else:
            self.status_var.set("Auto-generate disabled")
    
    def on_text_change(self, event=None):
        """Handle text changes and trigger auto-generation if enabled"""
        # Cancel any pending text change timer
        if self.text_modified_timer:
            self.root.after_cancel(self.text_modified_timer)
        
        # Set a new timer to wait for user to finish typing
        if self.auto_generate.get():
            self.text_modified_timer = self.root.after(1000, self.check_text_changes)
    
    def check_text_changes(self):
        """Check if text has changed and generate audio if needed"""
        current_text = self.text_area.get("1.0", tk.END).strip()
        if current_text != self.last_text and current_text:
            self.last_text = current_text
            self.generate_speech()
    
    def display_error(self, message):
        """Display error message with red color"""
        self.status_var.set(message)
        self.status_label.config(fg=self.error_color)
        
        # Set a timer to reset color after 5 seconds
        self.root.after(5000, self.reset_status_color)
    
    def reset_status_color(self):
        """Reset status label color to normal"""
        self.status_label.config(fg=self.dark_text)
        
    def generate_speech(self):
    
        self.play_background_music.set(False)
        
        # Disable generate button during generation
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=tk.DISABLED)
        
        self.status_var.set("Generating speech...")
        self.reset_status_color()  # Ensure normal text color
        self.root.update()
        
        # Get text and selected voice
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            self.status_var.set("Please enter some text")
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.configure(state=tk.NORMAL)
            return
        
        # Check if we have a valid voice selection
        selected_voice_name = self.voice_var.get()
        if not selected_voice_name or selected_voice_name not in self.voices:
            self.display_error("Please select a valid voice first")
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.configure(state=tk.NORMAL)
            return
            
        selected_voice_id = self.voices[selected_voice_name]
        
        # Get speech rate
        rate_percent = self.speech_rate.get()  # 0-100%
        
        # Convert to Edge TTS rate format (ranges from -100% to +100%)
        # Map 0-100 to -100-100 (0->-100, 50->0, 100->+100)
        rate_value = ((rate_percent / 50) - 1) * 100
        
        # Clean up old audio files
        current_folder = os.getcwd()
        for filename in os.listdir(current_folder):
            if filename.endswith(".mp3"):
                file_path = os.path.join(current_folder, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")
        
        # Generate audio in a separate thread
        threading.Thread(target=self.generate_speech_thread, 
                        args=(text, selected_voice_id, rate_value)).start()
    
    def generate_speech_thread(self, text, voice_id, rate):
        # Generate a random filename
        random_filename = str(random.getrandbits(32))
        output_file = f"output-{random_filename}.mp3"
        
        try:
            if isinstance(voice_id, tuple):  # Google TTS
                lang, tld = voice_id
                tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
                tts.save(output_file)
            else:  # Edge TTS
                async def generate_audio():
                    communicate = edge_tts.Communicate(text, voice_id, rate=f"{rate:+.0f}%")
                    await communicate.save(output_file)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_audio())
                loop.close()
            
            # Audio generated successfully
            self.root.after(0, lambda: self.speech_generated(output_file))
            
        except Exception as e:
            # Handle general errors
            error_message = str(e)
            self.root.after(0, lambda: self.handle_general_error(error_message))
    
    def handle_general_error(self, error_message):
        """Handle general errors"""
        # Display error message in red
        print(error_message)
        self.display_error(f"Error generating speech: {error_message}")
        
        # Re-enable buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=tk.NORMAL)
    
    
    
    def toggle_background_music(self):
        """Toggle background music on/off"""
        
        background_music_boolean = self.play_background_music.get()

        if background_music_boolean :
            # Start playing background music
            try:
                
                if self.background_music:
                    self.background_music.stop()

                # Check paths
                tinnitus_folder = os.path.join(self.directory_name, "tinnitus")
                music_path = os.path.join(tinnitus_folder, "relaxing_noise.mp3")
                
                if not os.path.exists(tinnitus_folder):
                    raise FileNotFoundError("'tinnitus' folder not found")
                
                if not os.path.exists(music_path):
                    raise FileNotFoundError("'relaxing_noise.mp3' not found in tinnitus folder")
                
                self.current_audio_file = music_path
                
                # Get accurate audio length using mutagen
                try:
                    audio = MP3(self.current_audio_file)
                    self.audio_length = audio.info.length
                    
                    # Update total time display
                    mins, secs = divmod(int(self.audio_length), 60)
                    self.total_time.configure(text=f" {mins}:{secs:02d}")
                except Exception as e:
                    print(f"Error getting audio length: {e}")
                    self.audio_length = 30  # Fallback to default
                
                # Enable player controls
                self.play_button.configure(state=tk.NORMAL)
                self.stop_button.configure(state=tk.NORMAL)
                
                # Enable the generate button again
                for widget in self.root.winfo_children():
                    if isinstance(widget, ttk.Button):
                        widget.configure(state=tk.NORMAL)
                        
                        
                self.play_audio()
                
                # Stop any currently playing background music
                
                
                # Load and play background music
                #self.background_music = pygame.mixer.Sound(music_path)
                # Set volume before playing
                #self.background_music.set_volume(0.3)
                # Play in infinite loop
                #self.background_music.play(loops=-1)
                
                self.status_var.set("Background music started")
                
            except Exception as e:
                self.play_background_music.set(False)
                self.display_error(f"Could not play background music: {str(e)}")
        else:
            # Stop background music
            
            self.stop_audio()
            #self.background_music = None
            self.current_audio_file = None
            self.is_playing = False
            self.status_var.set("Background music stopped")
        
        self.reset_status_color()
    
    
    
    def speech_generated(self, output_file):
        # Update status
        self.status_var.set("Speech generated successfully")
        self.reset_status_color()  # Ensure normal text color
        
        # Clean up previous file if exists
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                # Stop any playing audio first
                if self.is_playing:
                    self.stop_audio()
                
                # Delete the file
                os.remove(self.current_audio_file)
            except Exception as e:
                print(f"Error removing previous audio file: {e}")
        
        # Store the current audio file path
        self.current_audio_file = output_file
        
        # Get accurate audio length using mutagen
        try:
            audio = MP3(output_file)
            self.audio_length = audio.info.length
            
            # Update total time display
            mins, secs = divmod(int(self.audio_length), 60)
            self.total_time.configure(text=f"/ {mins}:{secs:02d}")
        except Exception as e:
            print(f"Error getting audio length: {e}")
            self.audio_length = 30  # Fallback to default
        
        # Enable player controls
        self.play_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.NORMAL)
        
        # Enable the generate button again
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=tk.NORMAL)
        
        # Play the audio automatically
        self.play_audio()
    
    def play_audio(self):
        if self.current_audio_file and not self.is_playing:
            # Load and play the audio
            mixer.music.load(self.current_audio_file)
            mixer.music.play()
            
            # Update button text
            self.play_button.configure(text="Pause")
            
            # Set playing flag
            self.is_playing = True
            
            # Reset pause position
            if self.paused_pos > 0:
                # If resuming from a pause, we need to set the position
                # However, pygame can't set position directly, so we'd need a different approach
                # For now, we're just going to restart and track our playing position
                self.paused_pos = 0
            
            # Track start time for progress calculations
            self.start_time = time.time()
            
            # Start progress updates
            self.update_progress()
    
    def toggle_play(self):
        if not self.current_audio_file:
            return

        if self.is_playing:
            # Pause playback
            mixer.music.pause()
            self.play_button.configure(text="Play")
            self.is_playing = False
            # Save current position for progress tracking
            self.paused_pos = time.time() - self.start_time
            # Cancel progress updates
            if hasattr(self, 'progress_update_id') and self.progress_update_id:
                self.root.after_cancel(self.progress_update_id)
                self.progress_update_id = None
        else:
            # Resume or start playback
            if self.paused_pos > 0:  # If paused, resume from the same position
                #mixer.music.unpause()
                #mixer.music.load(self.current_audio_file)
                mixer.music.play()
                time.sleep(0.1)  # Small delay to allow playback to start
                mixer.music.set_pos(self.paused_pos) 
    
                self.play_button.configure(text="Pause")
                self.is_playing = True
                # Adjust start_time to account for the already played time
                self.start_time = time.time() - self.paused_pos
                self.paused_pos = 0  # Reset paused position
                # Restart progress updates
                self.update_progress()
            else:  # Start from the beginning
                mixer.music.load(self.current_audio_file)
                mixer.music.play()
                self.start_time = time.time()
                self.is_playing = True
                self.play_button.configure(text="Pause")
                # Restart progress updates
                self.update_progress()
    
    def stop_audio(self):
        if not self.current_audio_file:
            return
            
        # Stop playback
        mixer.music.stop()
        self.play_button.configure(text="Play")
        self.is_playing = False
        
        # Reset tracking variables
        self.paused_pos = 0
        self.start_time = 0
        
        # Reset progress
        self.progress_var.set(0)
        self.current_time.configure(text="0:00")
        
        # Cancel progress updates
        if self.progress_update_id:
            self.root.after_cancel(self.progress_update_id)
            self.progress_update_id = None
    
    def update_progress(self):
        if self.is_playing:
            # Calculate current position based on real time elapsed
            current_time = time.time()
            pos_seconds = current_time - self.start_time
            
            # Check if playback has ended
            if pos_seconds >= self.audio_length:
                self.stop_audio()
                return
                
            # Update progress bar
            if self.audio_length > 0:
                progress = (pos_seconds / self.audio_length) * 100
                self.progress_var.set(progress)
            
            # Update time display
            mins, secs = divmod(int(pos_seconds), 60)
            self.current_time.configure(text=f"{mins}:{secs:02d}")
            
            # Schedule next update
            self.progress_update_id = self.root.after(100, self.update_progress)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()