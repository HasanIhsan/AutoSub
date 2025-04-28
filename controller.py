from tkinter import filedialog
from transcriber import Transcriber
from helpers import get_language_code, read_srt, preprocess_audio, refine_srt_with_aeneas
from exporter import Exporter
from previewWindow import PreviewWindow

import stable_whisper

#note:  1 sub per word, large, eng, 36 sec audio file takes (from start to refined SRT): 3:41 (so you can imagine it will take mushc longer for longer audio files) (3/19/25)
#note: the stop_process doens't actually stop the docker contianer!
class AutoSubsController:
    def __init__(self, ui):
        self.ui = ui
        self.audio_file = "output/processed_audio.wav"
        self.setup_connections()

    def setup_connections(self):
        self.ui.audio_source_button.config(command=self.select_audio_file)
        self.ui.start_process_button.config(command=self.start_process)
        # Connect re-export button
        self.ui.reexport_button.config(command=self.re_export)

        # Connect the privew button
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
        - Start gentle with docer (removed 4/22/2025)
        - get info from UI (like lang, word count, and so on)
        - pre-process the audio (pydub)
        - transcribe the audio (whisper)
        - output inital srt/text from whisper/pre process audio
        - refine the srt with gentel (forced alignment) ( takes in hard coded langauge=eng (will fix later))
        """


        language_str = self.ui.language_combo.get()
        language = get_language_code(language_str)
        model_size = self.ui.model_size_combo.get()
        try:
            words_per_subtitle = int(self.ui.words_per_subtitle_edit.get())
        except ValueError:
            words_per_subtitle = 1

        pause_threshold = 0.1  # seconds

        # Pre-process audio
        processed_audio = preprocess_audio(self.audio_file, output_file="output/processed_audio.wav")

        # Transcribe using the processed audio
        transcriber = Transcriber(model_size)
        result = transcriber.transcribe(processed_audio, language)

        #testing whispers builtin output SRT
        #result.to_srt_vtt('stable.srt')

        text_output_file = "output/transcript.txt"
        initial_srt_file = "output/transcript.srt"

        Exporter.save_transcription(result, text_output_file, words_per_subtitle)
        Exporter.export_srt(result, initial_srt_file, words_per_subtitle, pause_threshold)

        # Run forced alignment with Aeneas to refine SRT,
        # now passing words_per_subtitle for grouping.
        refined_srt_file = "output/refined_transcript.srt"

        # Forced alignment with Aeneas
        refine_srt_with_aeneas(processed_audio, text_output_file, refined_srt_file, language=language)

        subtitles = read_srt(refined_srt_file)
        self.ui.update_timeline(subtitles)

    def re_export(self):
        """
        Gather the current edited subtitles from the timeline and re-export the SRT.
        """
        # Build list of subtitles from UI subtitle_rows
        updated_subtitles = []
        for row in self.ui.subtitle_rows:
            start = row["start"]
            end = row["end"]
            text = row["edit"].get()
            updated_subtitles.append({"start": start, "end": end, "text": text})
        output_srt_file = "output/transcript_reexported.srt"
        Exporter.re_export_srt(updated_subtitles, output_srt_file)

    def preview_Transcript(self):
        """
            Called when the user clicks 'priview'
            for not just print, show message 4/24/2025
        """
        print(f"previewing audio: {self.audio_file}")

        # Ask user for which SRT to load
        #!! NOTE: Will make this Automatice in the future/give a radio button in the priview screen
        srt_path = filedialog.askopenfilename(
            title="Select SRT for preview", filetypes=[("SRT Files", "*.srt")]
        )

        #create and display the preiview window
        self.preview_win = PreviewWindow(self.ui, self.audio_file, srt_path)
        self.preview_win.grab_set()
