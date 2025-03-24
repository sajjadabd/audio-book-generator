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
from mutagen.mp3 import MP3  # Add this import for accurate audio length

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Application")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # Set dark theme colors
        self.dark_bg = "#1e1e1e"
        self.dark_secondary_bg = "#2d2d2d"
        self.gray_color = "#adacac"
        self.dark_text = "#e0e0e0"
        self.accent_color = "#007acc"  # Blue accent color
        self.error_color = "#ff5555"   # Red color for errors
        
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
        self.speech_rate = tk.IntVar(value=-20)  # Default to -20% (slower)
        
        # Text modification tracking
        self.last_text = ""
        self.text_modified_timer = None
        
        # Voice options
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
        }
        
        # Create UI elements
        self.create_widgets()
        
        # Setup progress update timer
        self.progress_update_id = None
    
    def setup_styles(self):
        """Set up ttk styles for dark theme"""
        style = ttk.Style()
        
        # Configure frame styles
        style.configure("TFrame", background=self.dark_bg)
        style.configure("TLabelframe", background=self.dark_bg, foreground=self.dark_text)
        style.configure("TLabelframe.Label", background=self.dark_bg, foreground=self.dark_text)
        
        # Configure label styles
        style.configure("TLabel", background=self.dark_bg, foreground=self.dark_text)
        
        # Configure button styles - with black foreground color
        style.configure("TButton", 
                       background=self.dark_secondary_bg, 
                       foreground="black",  # Changed to black
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor=self.accent_color)
        
        # Button hover and pressed states
        style.map("TButton", 
                 background=[("active", self.accent_color), 
                            ("pressed", self.accent_color)], 
                 foreground=[("active", "black"),  # Changed to black 
                            ("pressed", "black")])  # Changed to black
        
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
                       foreground="black",  # Changed to black
                       selectbackground=self.accent_color,
                       selectforeground="black")  # Changed to black
        
        # Set dropdown list colors (this requires tk option settings)
        self.root.option_add('*TCombobox*Listbox.background', self.gray_color)
        self.root.option_add('*TCombobox*Listbox.foreground', "black")  # Changed to black
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.accent_color)
        self.root.option_add('*TCombobox*Listbox.selectForeground', "black")  # Changed to black
        
        # Configure progress bar style
        style.configure("TProgressbar", 
                       background=self.accent_color,
                       troughcolor=self.dark_secondary_bg)
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Voice selection and rate control
        settings_frame = ttk.LabelFrame(main_frame, text="Voice Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # Voice dropdown
        voice_frame = ttk.Frame(settings_frame)
        voice_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(voice_frame, text="Select Voice:").pack(side=tk.LEFT, padx=5)
        
        self.voice_var = tk.StringVar()
        voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly", width=30)
        voice_dropdown['values'] = list(self.voices.keys())
        voice_dropdown.current(0)
        voice_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Speech rate control
        rate_frame = ttk.Frame(settings_frame)
        rate_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(rate_frame, text="Speech Rate:").pack(side=tk.LEFT, padx=5)
        
        def on_slider_change(value):
            # Round to nearest multiple of 5
            rounded_value = round(float(value) / 5) * 5
            # Set the variable to the rounded value
            self.speech_rate.set(rounded_value)
            
        # Speech rate slider
        rate_slider = ttk.Scale(rate_frame, 
                               from_=-50, 
                               to=50, 
                               orient=tk.HORIZONTAL, 
                               variable=self.speech_rate, 
                               length=200,
                               command=on_slider_change)
        rate_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Speech rate value display
        self.rate_display = ttk.Label(rate_frame, width=5)
        self.rate_display.pack(side=tk.LEFT, padx=5)
        
        # Update rate display function
        def update_rate_display(*args):
            val = self.speech_rate.get()
            if val > 0:
                self.rate_display.config(text=f"+{val}%")
            else:
                self.rate_display.config(text=f"{val}%")
                
        # Call initially and bind to variable changes
        update_rate_display()
        self.speech_rate.trace_add("write", update_rate_display)
        
        # Text input area with controls
        text_frame = ttk.LabelFrame(main_frame, text="Enter Text", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Controls above text area
        text_controls_frame = ttk.Frame(text_frame)
        text_controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Clear button
        clear_button = ttk.Button(text_controls_frame, text="Clear Text", command=self.clear_text)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Auto-generate checkbox
        auto_generate_check = ttk.Checkbutton(
            text_controls_frame, 
            text="Auto-generate on text change", 
            variable=self.auto_generate,
            command=self.toggle_auto_generate
        )
        auto_generate_check.pack(side=tk.RIGHT, padx=5)
        
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
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure scrollbar colors
        self.text_area.config(highlightbackground=self.dark_secondary_bg, 
                             highlightcolor=self.accent_color)
        
        # Bind text changes
        self.text_area.bind("<KeyRelease>", self.on_text_change)
        
        # Generate button
        generate_button = ttk.Button(main_frame, text="Generate Speech", command=self.generate_speech)
        generate_button.pack(pady=10)
        
        # Audio player frame
        player_frame = ttk.LabelFrame(main_frame, text="Audio Player", padding="5")
        player_frame.pack(fill=tk.X, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(player_frame, orient="horizontal", length=300, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Time display
        time_frame = ttk.Frame(player_frame)
        time_frame.pack(fill=tk.X, padx=5)
        
        self.current_time = ttk.Label(time_frame, text="0:00")
        self.current_time.pack(side=tk.LEFT)
        
        self.total_time = ttk.Label(time_frame, text="/ 0:00")
        self.total_time.pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = ttk.Frame(player_frame)
        control_frame.pack(pady=5)
        
        self.play_button = ttk.Button(control_frame, text="Play", command=self.toggle_play, state=tk.DISABLED)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_audio, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status label - changed to regular tk.Label to allow color changes
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, bg=self.dark_bg, fg=self.dark_text)
        self.status_label.pack(pady=5)
    
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
        
        selected_voice_name = self.voice_var.get()
        selected_voice = self.voices[selected_voice_name]
        
        # Get speech rate
        rate_value = self.speech_rate.get()
        rate_str = f"{rate_value}%"
        
        # Generate audio in a separate thread
        threading.Thread(target=self.generate_speech_thread, args=(text, selected_voice, rate_str)).start()
    
    def generate_speech_thread(self, text, voice, rate):
        # Generate a random filename
        random_filename = str(random.getrandbits(32))
        output_file = f"output-{random_filename}.mp3"
        
        # Generate speech using edge_tts
        async def generate():
            try:
                tts = edge_tts.Communicate(text, voice, rate=rate)
                await tts.save(output_file)
                
                # Update UI from the main thread
                self.root.after(0, lambda: self.speech_generated(output_file))
                
            except edge_tts.exceptions.NoAudioReceived:
                # Handle the specific error
                self.root.after(0, lambda: self.handle_no_audio_error())
                
            except Exception as e:
                # Handle other errors
                self.root.after(0, lambda: self.handle_general_error(str(e)))
        
        # Run the async function
        asyncio.run(generate())
    
    def handle_no_audio_error(self):
        """Handle NoAudioReceived error"""
        # Display error message in red
        self.display_error("No audio was received. The text may contain unsupported characters or the voice can't process it.")
        
        # Re-enable buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state=tk.NORMAL)
    
    def handle_general_error(self, error_message):
        """Handle general errors"""
        # Display error message in red
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
    
    def get_audio_length(self):
        """Get accurate length of the audio file"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            return 30  # Default fallback
            
        try:
            # Use mutagen to get accurate audio length
            audio = MP3(self.current_audio_file)
            return audio.info.length
        except Exception as e:
            print(f"Error getting audio length: {e}")
            return 30  # Fallback to default

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()