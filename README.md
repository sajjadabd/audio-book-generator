# Text-to-Speech Application

![App Screenshot](screenshot.png) *(Note: Add a screenshot of your application here)*

A Python-based Text-to-Speech (TTS) application with a graphical user interface that converts text to speech using either Microsoft Edge TTS or Google TTS voices. The application includes an audio player with playback controls, volume adjustment, and progress tracking. 

## Features

- **Multiple Voice Options**:
  - 30+ Microsoft Edge TTS voices (US, UK, Australian, and other accents)
  - 8 Google TTS voices (different languages and accents)
  
- **Speech Customization**:
  - Adjustable speech rate (0-100%)
  - Auto-generation option for instant playback when typing

- **Text Processing Tools**:
  - Clear Unicode/emojis from text
  - Remove Markdown formatting
  - Paste from clipboard
  - Clear text button

- **Audio Player**:
  - Play/Pause/Stop controls
  - Volume adjustment (+/- buttons)
  - Progress bar with seeking capability
  - Current/total time display

- **Dark Theme UI**:
  - Modern dark interface with accent colors
  - Responsive layout

## Installation

1. **Prerequisites**:
   - Python 3.7 or higher
   - pip package manager

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python player_main.pyw
   ```

## How to Use

1. **Enter Text**:
   - Type or paste your text into the text area
   - Use the text processing buttons if needed:
     - "Clear Unicode" - removes emojis and special characters
     - "Markdown to Text" - removes markdown formatting
     - "Paste" - pastes from clipboard
     - "Clear Text" - clears the text area

2. **Select Voice**:
   - Choose from the dropdown menu
   - Use the ▲/▼ buttons to navigate through voices

3. **Adjust Speech Rate**:
   - Use the slider to set speaking speed (0-100%)

4. **Generate Speech**:
   - Click "Generate Speech" or enable "Auto-generate" to automatically convert when typing

5. **Playback Controls**:
   - Use Play/Pause/Stop buttons
   - Adjust volume with +/- buttons
   - Click on the progress bar to seek to a specific position

## Troubleshooting

- **No audio playback**:
  - Ensure your system volume is not muted
  - Check that pygame is properly installed (`pip install pygame`)
  - Verify no other application is using the audio device

- **Edge TTS errors**:
  - Ensure you have an active internet connection
  - Try selecting a different voice

- **Google TTS errors**:
  - Some Google TTS voices may be region-restricted
  - Check your internet connection

## License

This project is open-source and available under the [MIT License](LICENSE).

## Future Improvements

- Save/Load text files
- Export audio files
- Voice pitch adjustment
- More text processing options
- Keyboard shortcuts

---

*Note: To complete this README, you should:*
1. *Add a screenshot of your application (save as screenshot.png in the same folder)*
2. *Create a LICENSE file if you want to specify terms*
3. *Adjust any specific instructions for your target users*