import whisper

# Load the best (largest) model for highest transcription accuracy.
model = whisper.load_model("large")

print('audio loaded!')
# Replace 'your_audio_file.ext' with your audio file's path (e.g., "audio.mp3").
audio_file = "audio/autosubs-exported-audio.wav"

print('Transcribing Audio...')
# Transcribe the audio file.
result = model.transcribe(audio_file)

# Save the transcribed text to a file.
with open("transcript.txt", "w") as f:
    f.write(result["text"])

print("Transcription complete. Check transcript.txt for the output.")
