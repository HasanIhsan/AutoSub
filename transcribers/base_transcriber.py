from abc import ABC, abstractmethod

class TranscriberBase(ABC):
    def __init__(self, model_size: str, language: str = "en"):
        self.model_size = model_size
        self.language = language

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict:
        """Return dict with 'segments' and/or .text"""
        pass