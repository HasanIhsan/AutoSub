from transcriber import Transcriber
from helpers import get_language_code
from exporter import Exporter
import json
 
def main():
    """Main function to load the model, transcribe, and save the results."""
    audio_file = "audio/audio-short.wav"
    text_output_file = "output/transcript.txt"
    srt_output_file = "output/transcript.srt"
    
    # Set how many words you want per subtitle (line)
    words_per_subtitle = 1  # Change this to any number you prefer (e.g., 3)
    
    # Choose the model size (e.g., "large", "medium", "small", "tiny")
    model_size = "large"
    
    Pause_thr = 0.1 # seconds, adjust as needed
       
    # Set language: either "detect" for auto-detection or a language like "english", "french", etc.
    language_input = "english"  # Change as needed.
    language = get_language_code(language_input)
    
    transcriber = Transcriber(model_size)
    result = transcriber.transcribe(audio_file, language)
  
    
    #print(json.dumps(result, indent=2))
    
    Exporter.save_transcription(result, text_output_file, words_per_subtitle)
    Exporter.export_srt(result, srt_output_file, words_per_subtitle, Pause_thr)

if __name__ == "__main__":
    main()
