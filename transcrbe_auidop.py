import whisper

def load_whisper_model(model_size):
    """Load the Whisper AI model with the best accuracy."""
    print("Loading Whisper model...")
    return whisper.load_model(model_size)

def get_language_code(language_str):
    """
    Convert a common language name to its ISO code.
    
    If the user enters "detect", returns None to allow auto-detection.
    """
    if language_str.lower() == "detect":
        return None
    
    # Mapping common language names to their ISO codes.
    language_mapping = {
        "english": "en",
        "french": "fr",
        "spanish": "es",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
        # Add additional mappings as needed.
    }
    # If the language is not in the mapping, assume the user provided a valid code.
    return language_mapping.get(language_str.lower(), language_str.lower())

def transcribe_audio(model, audio_path, language=None):
    """Transcribe the given audio file using the Whisper model."""
    print("Transcribing Audio...")
    # If language is None, Whisper will auto-detect the language.
    return model.transcribe(audio_path, language=language)

def save_transcription(transcription, output_file, words_per_subtitle=1):
    """
    Save the transcribed text to a file with a specified number of words per subtitle.
    
    Parameters:
      - transcription: The transcription result from Whisper.
      - output_file: The file path where the transcription will be saved.
      - words_per_subtitle: Number of words to group per line.
        For example, 3 will output 3 words per subtitle (line).
    """
    text = transcription["text"]
    
    if words_per_subtitle > 0:
        words = text.split()
        lines = [
            " ".join(words[i:i+words_per_subtitle])
            for i in range(0, len(words), words_per_subtitle)
        ]
        text = "\n".join(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Transcription saved to {output_file}")

def format_timestamp(seconds):
    """Convert seconds (float) into an SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def export_srt(transcription, output_srt_file):
    """
    Export the transcription segments as a SRT file.
    
    Parameters:
      - transcription: The transcription result from Whisper (must include 'segments').
      - output_srt_file: The file path where the SRT file will be saved.
    """
    segments = transcription.get("segments", [])
    with open(output_srt_file, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(segments, start=1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
    print(f"SRT file saved to {output_srt_file}")

def main():
    """Main function to load the model, transcribe, and save the result."""
    audio_file = "audio/autosubs-exported-audio.wav"
    text_output_file = "transcript.txt"
    srt_output_file = "transcript.srt"
    
    # Set how many words you want per subtitle (line) for the text transcript.
    words_per_subtitle = 1  # Change this to any number you prefer

    # Choose the model size (e.g., "large", "medium", "small", "tiny")
    model_size = "large"
    
    # For language, the user can enter a common language name (like "english", "french")
    # or "detect" to allow auto-detection.
    language_input = "english"  # e.g., change to "detect" or another language.
    language = get_language_code(language_input)
    
    model = load_whisper_model(model_size)
    result = transcribe_audio(model, audio_file, language)
    
    save_transcription(result, text_output_file, words_per_subtitle)
    export_srt(result, srt_output_file)

if __name__ == "__main__":
    main()
