import whisper

def load_whisper_model():
    """Load the Whisper AI model with the best accuracy."""
    print("Loading Whisper model...")
    return whisper.load_model("large")

def transcribe_audio(model, audio_path):
    """Transcribe the given audio file using the Whisper model."""
    print("Transcribing Audio...")
    return model.transcribe(audio_path)

def save_transcription(transcription, output_file, one_word_per_line=False):
    """
    Save the transcribed text to a file.
    
    - If `one_word_per_line` is True, each word appears on a new line.
    - Otherwise, the full sentence is written normally.
    """
    text = transcription["text"]
    
    if one_word_per_line:
        words = text.split()  # Split text into words
        text = "\n".join(words)  # Join with newline for 1 word per line

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Transcription saved to {output_file}")

def main():
    """Main function to load the model, transcribe, and save the result."""
    audio_file = "audio/autosubs-exported-audio.wav"
    output_file = "transcript.txt"
    one_word_per_line = True  # Change this to False if you want normal output

    model = load_whisper_model()
    result = transcribe_audio(model, audio_file)
    save_transcription(result, output_file, one_word_per_line)

if __name__ == "__main__":
    main()
