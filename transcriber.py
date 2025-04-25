import stable_whisper

class Transcriber:
    def __init__(self, model_size):
        """Initialize and load the Stable Whisper model. (Updated 4/22/25)"""
        self.model_size = model_size
        self.model = self.load_model()

    def load_model(self):
        """Load the Stable Whisper model with high accuracy. (Updated 4/22/25)"""
        print("Loading Stable Whisper model...")
        return stable_whisper.load_model(self.model_size)

    def transcribe(self, audio_path, language=None):
        """
        Transcribe the given audio file using Stable Whisper with word timestamps.
        If `language` is None, automatic language detection is used.
        (Updated 4/22/25)
        """
        print("Transcribing Audio using Stable Whisper...")
        return self.model.transcribe(audio_path, language=language, word_timestamps=True)
