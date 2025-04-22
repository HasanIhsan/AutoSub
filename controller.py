from tkinter import filedialog
from transcriber import Transcriber
from helpers import get_language_code, read_srt, preprocess_audio, refine_srt_with_gentle, docker_gentle_process
from exporter import Exporter

#note:  1 sub per word, large, eng, 36 sec audio file takes (from start to refined SRT): 3:41 (so you can imagine it will take mushc longer for longer audio files) (3/19/25)
#note: the stop_process doens't actually stop the docker contianer!
class AutoSubsController:
    def __init__(self, ui):
        self.ui = ui
        self.audio_file = "default_audio.wav"
        self.gentle_process = None  # Store the Gentle process if launched
        self.setup_connections()

    def setup_connections(self):
        self.ui.audio_source_button.config(command=self.select_audio_file)
        self.ui.start_process_button.config(command=self.start_process)
        # Connect re-export button
        self.ui.reexport_button.config(command=self.re_export)

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
        - Start gentle with docer
        - get info from UI (like lang, word count, and so on)
        - pre-process the audio (pydub)
        - transcribe the audio (whisper)
        - output inital srt/text from whisper/pre process audio
        - refine the srt with gentel (forced alignment) ( takes in hard coded langauge=eng (will fix later))
        """
        # Check if Gentle is already running; if not, launch it via Docker.
        if self.gentle_process is None:
            try:
                self.gentle_process = docker_gentle_process()
            except Exception as e:
                print("Error launching Gentle via Docker:", e)
                # Depending on your needs, you might want to abort or continue here.
        
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

        text_output_file = "output/transcript.txt"
        initial_srt_file = "output/transcript.srt"

        Exporter.save_transcription(result, text_output_file, words_per_subtitle)
        Exporter.export_srt(result, initial_srt_file, words_per_subtitle, pause_threshold)

        # Run forced alignment with Gentle to refine SRT,
        # now passing words_per_subtitle for grouping.
        refined_srt_file = "output/refined_transcript.srt"
        refine_srt_with_gentle(processed_audio, text_output_file, refined_srt_file, language="eng", words_per_subtitle=words_per_subtitle)

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

    def stop_gentle(self):
        """Stop the Gentle Docker process if it is running."""
        if self.gentle_process is not None:
            try:
                print("Stopping Gentle Docker process...")
                self.gentle_process.kill()
                self.gentle_process = None
            except Exception as e:
                print("Error stopping Gentle Docker process:", e)
