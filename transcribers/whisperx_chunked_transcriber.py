import os
from pydub import AudioSegment
import whisperx
from .base_transcriber import TranscriberBase
from utils.srt_utils import write_srt_n_words

class WhisperXChunkedTranscriber(TranscriberBase):
    def transcribe(self, audio_path: str) -> dict:
        chunk_len = 60
        stem = os.path.splitext(os.path.basename(audio_path))[0]
        folder = os.path.join(os.path.dirname(audio_path) or ".", stem)
        os.makedirs(folder, exist_ok=True)

        audio = AudioSegment.from_file(audio_path)
        chunks = []
        for i, start_ms in enumerate(range(0, len(audio), chunk_len * 1000)):
            seg = audio[start_ms:start_ms + chunk_len * 1000]
            wav_path = os.path.join(folder, f"chunk_{i:03}.wav")
            seg.export(wav_path, format="wav")
            chunks.append((wav_path, start_ms / 1000.0))

        device = "cpu"
        model = whisperx.load_model(self.model_size, device, compute_type="int8")
        align_model, metadata = whisperx.load_align_model(self.language, device)

        all_segments = []
        for idx, (fpath, offset) in enumerate(chunks):
            wav = whisperx.load_audio(fpath)
            res = model.transcribe(wav, batch_size=1, language=self.language)
            aligned = whisperx.align(res["segments"], align_model, metadata, wav, device=device)

            for seg in aligned["segments"]:
                for w in seg["words"]:
                    w["start"] += offset
                    w["end"] += offset
                all_segments.append(seg)

        write_srt_n_words(
            {"segments": all_segments},
            audio_path,
            "output/whisperx_transcript.srt",
            words_per_subtitle=1
        )
        print(f"Chunked WhisperX done.")
        return {"segments": all_segments}