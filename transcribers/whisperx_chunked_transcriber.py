import os
from pydub import AudioSegment
import whisperx
from .base_transcriber import TranscriberBase
from utils.srt_utils import write_srt_n_words

class WhisperXChunkedTranscriber(TranscriberBase):
    def transcribe(self, audio_path: str) -> dict:
        chunk_len = 60 # 60 seconds per chunk
        
        #prep chuck folder
        stem = os.path.splitext(os.path.basename(audio_path))[0]
        folder = os.path.join(os.path.dirname(audio_path) or ".", stem)
        os.makedirs(folder, exist_ok=True)

        # 1) Split into chunks
        print(f"Chunking audio file {audio_path} into {chunk_len} second segments...")
        
        audio = AudioSegment.from_file(audio_path)
        chunks = []
        for i, start_ms in enumerate(range(0, len(audio), chunk_len * 1000)):
            seg = audio[start_ms:start_ms + chunk_len * 1000]
            wav_path = os.path.join(folder, f"chunk_{i:03}.wav")
            seg.export(wav_path, format="wav")
            chunks.append((wav_path, start_ms / 1000.0))

        device = "cpu"
        
        # 2) Load models once
        #TODO: make model loading configurable (so i don't have to load model every new transcription)
        print(f"[WhisperX] Loading Whisper model '{self.model_size}' on {device}...")
        model = whisperx.load_model(self.model_size, device, compute_type="int8")
        align_model, metadata = whisperx.load_align_model(self.language, device)

        # 3) For each chunk, transcribe, align, offset *word* times, and write chunk-SRT
        all_segments = []
        for idx, (fpath, offset) in enumerate(chunks):
            wav = whisperx.load_audio(fpath)
            res = model.transcribe(wav, batch_size=1, language=self.language)
            aligned = whisperx.align(res["segments"], align_model, metadata, wav, device=device)

            # Offset *every word* in each segment by the chunk start
            for seg in aligned["segments"]:
                for w in seg["words"]:
                    w["start"] += offset
                    w["end"] += offset
                all_segments.append(seg)
                
            # Write this chunk’s SRT right away
            chunk_srt_path = os.path.join(folder, f"chunk_{idx:03}.srt")
            write_srt_n_words(
                {"segments": aligned["segments"]},
                fpath,
                chunk_srt_path,
                words_per_subtitle=1 # TODO: make this configurable (so i don't have to re-run)
            )

        # 4) Write the final SRT with all segments
        print(f"Writing final SRT with {len(all_segments)} segments...")
        write_srt_n_words(
            {"segments": all_segments},
            audio_path,
            "output/whisperx_transcript.srt",
            words_per_subtitle=1 #TODO: make this value configurable from UI
        )
        print(f"Chunked WhisperX done.")
        return {"segments": all_segments}