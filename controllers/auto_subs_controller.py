import re  # ❌ UNUSED but kept for any future regex use
from tkinter import filedialog

from transcribers.base_transcriber import TranscriberBase
from transcribers.stable_whisper_transcriber import StableWhisperTranscriber
from transcribers.whisperx_transcriber import WhisperXTranscriber
from transcribers.whisperx_chunked_transcriber import WhisperXChunkedTranscriber
from preprocessors.audio_preprocessor import AudioPreprocessor
from utils.lang_utils import get_language_code
from utils.srt_utils import read_srt, smooth_srt
from exporters.exporter import Exporter
from preview_window import PreviewWindow

# note: 1 sub per word, large, eng, 36 sec audio file takes ~3:41 (3/19/25)
# note: stop_process doesn’t actually stop the docker container!
class AutoSubsController:
    def __init__(self, ui):
        self.ui = ui
        self.audio_file = "output/processed_audio.wav"
        self.setup_connections()

    def setup_connections(self):
        self.ui.audio_source_button.config(command=self.select_audio_file)
        self.ui.start_process_button.config(command=self.start_process)
        self.ui.reexport_button.config(command=self.re_export)
        self.ui.priview_button.config(command=self.preview_Transcript)

    def select_audio_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("WAV Files", "*.wav")]
        )
        if file_path:
            self.audio_file = file_path
            self.ui.audio_file_label.config(text=file_path)
        else:
            self.audio_file = "default_audio.wav"
            self.ui.audio_file_label.config(text="default_audio.wav")

    def start_process(self):
        """
        steps for processing:
        - get info from UI (lang, word count, etc.)
        - pre-process the audio (pydub + sox)
        - transcribe the audio
        - refine via forced alignment
        """
         
        language_str = self.ui.language_combo.get()
        language = get_language_code(language_str)
        model_size = self.ui.model_size_combo.get()
        transcriber_s = self.ui.transciber_s_combo.get()
        
        try:
            words_per_subtitle = int(self.ui.words_per_subtitle_edit.get())
        except ValueError:
            words_per_subtitle = 1

        # Pre-process audio
        preprocessor = AudioPreprocessor()
        processed_audio = preprocessor.process(
            self.audio_file,
            output_file=f"output/{self.audio_file}"
        )

        # Choose transcriber
        if transcriber_s.startswith("whisperx-chunked"):
            transcriber: TranscriberBase = WhisperXChunkedTranscriber(model_size, language)
        elif transcriber_s.startswith("whisperx"):
            transcriber = WhisperXTranscriber(model_size, language)
        else:
            transcriber = StableWhisperTranscriber(model_size, language)

        # Transcribe & align
        aligned = transcriber.transcribe(processed_audio)

        # If using chunked whisperx, .transcribe writes the SRT itself.
        # Now smooth and re-export
        subtitles = read_srt("output/whisperx_transcript.srt")
        smoothed = smooth_srt(subtitles, min_gap=0.1, min_duration=0.5)
        Exporter.re_export_srt(smoothed, "output/refinedT.srt")
        self.ui.update_timeline(smoothed)

    def re_export(self):
        """
        Re-export edited subtitles from UI.
        """
        updated_subs = []
        for row in self.ui.subtitle_rows:
            updated_subs.append({
                "start": row["start"],
                "end": row["end"],
                "text": row["edit"].get()
            })
        Exporter.re_export_srt(updated_subs, "output/transcript_reexported.srt")

    def preview_Transcript(self):
        """
        Called when the user clicks 'priview' (4/24/2025)
        """
        print(f"previewing audio: {self.audio_file}")
        srt_path = filedialog.askopenfilename(
            title="Select SRT for preview", filetypes=[("SRT Files", "*.srt")]
        )
        self.preview_win = PreviewWindow(self.ui, self.audio_file, srt_path)
        self.preview_win.grab_set()