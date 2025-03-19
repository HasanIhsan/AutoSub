from PyQt5.QtWidgets import QFileDialog
from transcriber import Transcriber
from helpers import get_language_code, read_srt, preprocess_audio, refine_srt_with_gentle
from exporter import Exporter

class AutoSubsController:
    def __init__(self, ui):
        self.ui = ui
        self.audio_file = "default_audio.wav"
        self.setup_connections()

    def setup_connections(self):
        self.ui.audio_source_button.clicked.connect(self.select_audio_file)
        self.ui.start_process_button.clicked.connect(self.start_process)
        # Connect re-export button
        self.ui.reexport_button.clicked.connect(self.re_export)

    def select_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Select Audio File",
            "",
            "WAV Files (*.wav)"
        )
        if file_path:
            self.audio_file = file_path
            self.ui.audio_file_label.setText(file_path)
        else:
            self.audio_file = "default_audio.wav"
            self.ui.audio_file_label.setText("default_audio.wav")

    def start_process(self):
        language_str = self.ui.language_combo.currentText()
        language = get_language_code(language_str)
        model_size = self.ui.model_size_combo.currentText()
        try:
            words_per_subtitle = int(self.ui.words_per_subtitle_edit.text())
        except ValueError:
            words_per_subtitle = 1
            
        pause_threshold = 0.1  # seconds

        # Pre-process audio
        processed_audio = preprocess_audio(self.audio_file, output_file="output/processed_audio.wav")
        
        # Transcribe using the processed audio
        transcriber = Transcriber(model_size)
        result = transcriber.transcribe(processed_audio, language)

        text_output_file = "output/transcript.txt"
        initial_srt_file = "output/transcript.srt"

        Exporter.save_transcription(result, text_output_file, words_per_subtitle)
        Exporter.export_srt(result, initial_srt_file, words_per_subtitle, pause_threshold)

        # Run forced alignment with Gentle to refine SRT
        refined_srt_file = "output/refined_transcript.srt"
        refine_srt_with_gentle(processed_audio, text_output_file, refined_srt_file, language="eng")

        subtitles = read_srt(refined_srt_file)
        self.ui.update_timeline(subtitles)

    def re_export(self):
        """
        Gather the current edited subtitles from the timeline and re-export the SRT.
        """
        # Build list of subtitles from UI subtitle_rows
        updated_subtitles = []
        for row in self.ui.subtitle_rows:
            # The time info is stored as in the label; assume format "start --> end"
            # We'll use it as-is.
            start_end_text = row["edit"].parent().layout().itemAt(0).widget().text() # time_label text
            # Split to get start and end
            if "-->" in start_end_text:
                start, end = [s.strip() for s in start_end_text.split("-->")]
            else:
                start, end = "", ""
            # Get updated text from the QLineEdit
            text = row["edit"].text()
            updated_subtitles.append({"start": start, "end": end, "text": text})
        output_srt_file = "output/transcript_reexported.srt"
        Exporter.re_export_srt(updated_subtitles, output_srt_file)
