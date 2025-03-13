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
    
    language_mapping = {
        "english": "en",
        "french": "fr",
        "spanish": "es",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
        # Add additional mappings as needed.
    }
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

def export_srt(transcription, output_srt_file, words_per_subtitle):
    """
    Export the transcription segments as an SRT file with a specified number 
    of words per subtitle. For each segment, the function splits the text into 
    groups of words and divides the segment's time range evenly across those groups.
    
    Parameters:
      - transcription: The transcription result from Whisper (with 'segments').
      - output_srt_file: The file path where the SRT file will be saved.
      - words_per_subtitle: Number of words per subtitle line.
    """
    segments = transcription.get("segments", [])
    srt_index = 1
    with open(output_srt_file, "w", encoding="utf-8") as f:
        for segment in segments:
            seg_start = segment["start"]
            seg_end = segment["end"]
            seg_text = segment["text"].strip()
            if not seg_text:
                continue
            words = seg_text.split()
            # Calculate number of groups (subtitles) in this segment.
            n_groups = (len(words) + words_per_subtitle - 1) // words_per_subtitle
            # Divide the segment's duration evenly among groups.
            if n_groups == 0:
                continue
            group_duration = (seg_end - seg_start) / n_groups
            for i in range(n_groups):
                group_words = words[i*words_per_subtitle:(i+1)*words_per_subtitle]
                group_text = " ".join(group_words)
                group_start = seg_start + i * group_duration
                group_end = seg_start + (i+1) * group_duration
                start_str = format_timestamp(group_start)
                end_str = format_timestamp(group_end)
                f.write(f"{srt_index}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{group_text}\n\n")
                srt_index += 1
    print(f"SRT file saved to {output_srt_file}")

def main():
    """Main function to load the model, transcribe, and save the results."""
    audio_file = "audio/autosubs-exported-audio.wav"
    text_output_file = "transcript.txt"
    srt_output_file = "transcript.srt"
    
    # Set how many words you want per subtitle (line)
    words_per_subtitle = 1  # Change this to any number you prefer (e.g., 3)

    # Choose the model size (e.g., "large", "medium", "small", "tiny")
    model_size = "large"
    
    # Set language: either "detect" for auto-detection or a language like "english", "french", etc.
    language_input = "english"  # Change as needed.
    language = get_language_code(language_input)
    
    model = load_whisper_model(model_size)
    result = transcribe_audio(model, audio_file, language)
    
    save_transcription(result, text_output_file, words_per_subtitle)
    export_srt(result, srt_output_file, words_per_subtitle)

if __name__ == "__main__":
    main()
