import whisperx
import os
from whisperx.utils import get_writer
from .base_transcriber import TranscriberBase

class WhisperXTranscriber(TranscriberBase):
    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe + align audio with WhisperX, writing a word-level SRT.

        Parameters:
        - audio_path: Path to your .wav (or other) file.
        - model_name: one of whisper models ("small", "medium", "large", etc).
        - language: ISO lang code (e.g. "en"), or None for auto-detect.
        - device: "cuda" or "cpu".
        - output_srt: where to save the word-aligned SRT.

        Returns:
        - the aligned result dict. (5/1/2025)
        """
        
        device = "cpu"
        print(f"[WhisperX] Loading Whisper model '{self.model_size}' on {device}…")
        model = whisperx.load_model(self.model_size, device, compute_type="int8")
        audio = whisperx.load_audio(audio_path)

        print(f"[WhisperX] Transcribing {audio_path}…")
        result = model.transcribe(audio, language=self.language)

        print("[WhisperX] Loading alignment model…")
        align_model, metadata = whisperx.load_align_model(
            language_code=self.language or result["language"],
            device=device
        )

        print("[WhisperX] Running forced alignment…")
        result_aligned = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio,
            device=device
        )
        result_aligned["language"] = result["language"]

        vtt_dir = os.path.dirname("output/whisperx_transcript.srt") or "."
        os.makedirs(vtt_dir, exist_ok=True)
        vtt_writer = get_writer("srt", vtt_dir)
        vtt_writer(
            result_aligned,
            audio_path,
            {"max_line_width": 5, "max_line_count": 1, "highlight_words": False}
        )
        return result_aligned