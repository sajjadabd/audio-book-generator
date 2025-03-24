import tkinter as tk
from tkinter import scrolledtext, ttk
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
        mixer.init()
        
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
        self.speech_rate = tk.IntVar(value=50)  # Default to medium rate
        
        # Text modification tracking
        self.last_text = ""
        self.text_modified_timer = None
        
        # Edge TTS voices - Using predefined list of voices
        self.voices = {
            # United States (English)
            "US Female (Jenny)": "en-US-JennyNeural",
            "US Female (Aria)": "en-US-AriaNeural",
            "US Female (Ana)": "en-US-AnaNeural",
            "US Female (Michelle)": "en-US-MichelleNeural",
            "US Female (Sara)": "en-US-SaraNeural",
            "US Male (Guy)": "en-US-GuyNeural",
            "US Male (Davis)": "en-US-DavisNeural",
            "US Male (Jason)": "en-US-JasonNeural",
            "US Male (Tony)": "en-US-TonyNeural",
            "US Male (Andrew)": "en-US-AndrewNeural",
            
            # United Kingdom (English)
            "UK Female (Sonia)": "en-GB-SoniaNeural",
            "UK Female (Libby)": "en-GB-LibbyNeural",
            "UK Female (Mia)": "en-GB-MiaNeural",
            "UK Female (Abbie)": "en-GB-AbbieNeural",
            "UK Male (Ryan)": "en-GB-RyanNeural",
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
            
            "New Zealand Female (Molly)": "en-NZ-MollyNeural",
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
    
    def setup_styles(self):
        """Set up ttk styles for dark theme"""
        style = ttk.Style()
    
        # Set the theme to clam for better styling control
        style.theme_use("clam")
        
        # Configure frame styles
        style.configure("TFrame", background=self.dark_bg)
        style.configure("TLabelframe", background=self.dark_bg, foreground=self.dark_text)
        style.configure("TLabelframe.Label", background=self.dark_bg, foreground=self.dark_text)
        
        # Configure label styles
        style.configure("TLabel", background=self.dark_bg, foreground=self.dark_text)
        
        # Configure button styles - with black foreground color
        style.configure("TButton", 
                       background=self.gray_color, 
                       foreground="black",
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor=self.accent_color)
        
        # Button hover and pressed states
        style.map("TButton", 
                 background=[("active", self.accent_color), 
                            ("pressed", self.accent_color)], 
                 foreground=[("active", "black"),
                            ("pressed", "black")])
        
        # Configure checkbox styles
        style.configure("TCheckbutton", 
                       background=self.dark_bg, 
                       foreground=self.dark_text)
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
                       selectforeground="black")
        
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
        
        # Configure progress bar style
        style.configure("TProgressbar", 
                       background=self.accent_color,
                       troughcolor=self.dark_secondary_bg)
        
        # Small button style
        style.configure('Small.TButton', padding=(2, 0))
    
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
        
        # Auto-generate checkbox
        auto_generate_check = ttk.Checkbutton(
            text_controls_frame, 
            text="Auto-generate on text change", 
            variable=self.auto_generate,
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
            selectforeground=self.dark_text
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=ButtonXPadding, pady=ButtonYPadding)
        
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
        
        self.play_button = ttk.Button(control_frame, text="Play", command=self.toggle_play, state=tk.DISABLED, cursor='hand2', style='Small.TButton')
        self.play_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_audio, state=tk.DISABLED, cursor='hand2', style='Small.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=ButtonXPadding)
        
        # Status label - changed to regular tk.Label to allow color changes
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Select a voice and enter text.")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, bg=self.dark_bg, fg=self.dark_text)
        self.status_label.pack(pady=ButtonYPadding)
    
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
            
            # Save current position for proper progress tracking
            self.paused_pos = time.time() - self.start_time
            
            # Cancel progress updates
            if self.progress_update_id:
                self.root.after_cancel(self.progress_update_id)
                self.progress_update_id = None
        else:
            # Resume or start playback
            if self.paused_pos > 0:  # If paused
                mixer.music.unpause()
                # Update start time to account for paused duration
                self.start_time = time.time() - self.paused_pos
            else:  # Start from beginning
                mixer.music.load(self.current_audio_file)
                mixer.music.play()
                self.start_time = time.time()
                
            self.play_button.configure(text="Pause")
            self.is_playing = True
            
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