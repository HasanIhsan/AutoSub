import whisper

class Transcriber:
    def __init__(self, model_size):
        """Initialize and load the Whisper model. (3/13/25)"""
        self.model_size = model_size
        self.model = self.load_model()
    
    def load_model(self):
        """Load the Whisper AI model with the best accuracy. (3/13/25)"""
        print("Loading Whisper model...")
        return whisper.load_model(self.model_size)
    
    def transcribe(self, audio_path, language=None):
        """Transcribe the given audio file using the Whisper model. (3/13/25)"""
        print("Transcribing Audio...")
        return self.model.transcribe(audio_path, language=language, word_timestamps=True)
