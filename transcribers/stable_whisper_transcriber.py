import stable_whisper
from .base_transcriber import TranscriberBase

class StableWhisperTranscriber(TranscriberBase):
    def __init__(self, model_size, language=None):
        super().__init__(model_size, language)
        print("Loading Stable Whisper model...")
        self.model = stable_whisper.load_model(self.model_size)

    def transcribe(self, audio_path: str) -> dict:
        print("Transcribing Audio using Stable Whisper...")
        return self.model.transcribe(
            audio_path,
            language=self.language,
            word_timestamps=True
        )