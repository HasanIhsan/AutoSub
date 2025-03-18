from PyQt5.QtWidgets import QFileDialog
from transcriber import Transcriber
from helpers import get_language_code
from exporter import Exporter

class AutoSubsController:
    def __init__(self, ui):
        """
        Initialize with a reference to the UI (MainWindow).
        """
        self.ui = ui
        # Default audio file if none is selected
        self.audio_file = "default_audio.wav"
        self.setup_connections()

    def setup_connections(self):
        # When user clicks "Add Audio Input"
        self.ui.audio_source_button.clicked.connect(self.select_audio_file)
        # When user clicks "Start Process"
        self.ui.start_process_button.clicked.connect(self.start_process)

    def select_audio_file(self):
        """Open file dialog to select a WAV file and update the label."""
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
        """
        Read all settings from the UI and call the transcriber/exporter functions.
        """
        # Read language selection from dropdown
        language_str = self.ui.language_combo.currentText()
        language = get_language_code(language_str)
        
        # Read model size from dropdown
        model_size = self.ui.model_size_combo.currentText()
        
        # Get words per subtitle from the text box (fallback to 1 if invalid)
        try:
            words_per_subtitle = int(self.ui.words_per_subtitle_edit.text())
        except ValueError:
            words_per_subtitle = 1

        # (Optional) Set a pause threshold for splitting subtitles.
        pause_threshold = 0.1  # seconds

        # Instantiate the transcriber with the chosen model size.
        transcriber = Transcriber(model_size)
        result = transcriber.transcribe(self.audio_file, language)
        
        # Define output file paths (these could also be exposed in the UI if desired)
        text_output_file = "output/transcript.txt"
        srt_output_file = "output/transcript.srt"

        # Save plain transcription and export SRT using your exporter functions.
        Exporter.save_transcription(result, text_output_file, words_per_subtitle)
        Exporter.export_srt(result, srt_output_file, words_per_subtitle, pause_threshold)
