import whisper

def load_whisper_model():
    """Load the Whisper AI model with the best accuracy."""
    print("Loading Whisper model...")
    return whisper.load_model("large")

def transcribe_audio(model, audio_path):
    """Transcribe the given audio file using the Whisper model."""
    print("Transcribing Audio...")
    return model.transcribe(audio_path)

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
    
    # If words_per_subtitle is set to a positive integer, format the text accordingly.
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

def main():
    """Main function to load the model, transcribe, and save the result."""
    audio_file = "audio/autosubs-exported-audio.wav"
    output_file = "transcript.txt"
    
    # Set how many words you want per subtitle (line)
    words_per_subtitle = 3  # Change this to any number you prefer

    
    
    model = load_whisper_model()
    result = transcribe_audio(model, audio_file)
    save_transcription(result, output_file, words_per_subtitle)

if __name__ == "__main__":
    main()
