import whisper

class Transcriber:
    def __init__(self, model_size="large"):
        """Initialize and load the Whisper model."""
        self.model_size = model_size
        self.model = self.load_model()
    
    def load_model(self):
        """Load the Whisper AI model with the best accuracy."""
        print("Loading Whisper model...")
        return whisper.load_model(self.model_size)
    
    def transcribe(self, audio_path, language=None):
        """Transcribe the given audio file using the Whisper model."""
        print("Transcribing Audio...")
        # If language is None, Whisper will auto-detect the language.
        return self.model.transcribe(audio_path, language=language)
