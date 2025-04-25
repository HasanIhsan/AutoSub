
import subprocess
import time

from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from pydub import AudioSegment

def get_language_code(language_str):
    """
    Convert a common language name to its ISO code.
    If the user enters "detect", returns None to allow auto-detection.
    """
    if language_str.lower() == "detect":
        return None

    language_mapping = {
        "english": "en",
        "french": "fr",
        "spanish": "es",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
    }
    return language_mapping.get(language_str.lower(), language_str.lower())

def format_timestamp(seconds):
    """
    Convert seconds (float) into an SRT timestamp format (HH:MM:SS,mmm).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def read_srt(file_path):
    """
    Read an SRT file and return a list of subtitle entries.
    Each entry is a dictionary with keys: index, start, end, text.
    """
    subtitles = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        blocks = content.split("\n\n")
        for block in blocks:
            lines = block.splitlines()
            if len(lines) >= 3:
                idx = lines[0].strip()
                times = lines[1].strip()
                if "-->" in times:
                    start, end = times.split("-->")
                    start = start.strip()
                    end = end.strip()
                else:
                    start, end = "", ""
                text = " ".join(line.strip() for line in lines[2:])
                subtitles.append({"index": idx, "start": start, "end": end, "text": text})
    except Exception as e:
        print("Error reading SRT:", e)
    return subtitles

def preprocess_audio(input_file, output_file="output/processed_audio.wav"):
    """
    Pre-process the audio file by converting it to mono and normalizing its volume.
    Requires pydub. (3/18/25)
    """
    try:
        audio = AudioSegment.from_file(input_file, format="wav")
        # Convert to mono
        audio = audio.set_channels(1)
        # Normalize volume (for example, to -20 dBFS)
        change_in_dBFS = -20.0 - audio.dBFS
        normalized_audio = audio.apply_gain(change_in_dBFS)
        normalized_audio.export(output_file, format="wav")
        print(f"Pre-processed audio saved to {output_file}")
        return output_file
    except Exception as e:
        print("Error during audio pre-processing:", e)
        return input_file  # Fallback to original file if processing fails

def refine_srt_with_aeneas(audio_path, transcript_path, output_path, language="eng"):
    """
    Uses Aeneas to align transcript with audio and output an SRT.
    """
    config_string = f"task_language={language}|os_task_file_format=srt|is_text_type=plain"
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_path
    task.text_file_path_absolute = transcript_path
    task.sync_map_file_path_absolute = output_path

    ExecuteTask(task).execute()
    task.output_sync_map_file()
    print(f"Refined SRT written to {output_path}")
