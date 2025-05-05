
import subprocess
import time
import re
from datetime import timedelta, datetime

from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from pydub import AudioSegment
import noisereduce as nr
import numpy as np

import os
import torch
import whisperx
from whisperx.utils import get_writer


from whisperx.utils import format_timestamp as _fmt_ts
from typing import List, Dict


_TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}$')

_TIME_FMT = "%H:%M:%S,%f"  # Python’s strptime/strftime needs %f for microseconds
_BLOCK_RE = re.compile(r"(\d+)\s+([\d:,]+)\s+-->\s+([\d:,]+)\s+(.*)", re.DOTALL)

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

        #export a temp wav file for noise reduction
        temp_path = "output/temp_for_noise.wav"
        normalized_audio.export(temp_path, format="wav")

        #load with numpy
        from scipy.io import wavfile
        rate, data = wavfile.read(temp_path)

        #apply noise reduction
        reduced_noise = nr.reduce_noise(y=data, sr=rate)

        #save final output
        wavfile.write(output_file, rate, reduced_noise.astype(np.int16))

        print(f"Pre-processed audio saved to {output_file}")
        return output_file
    except Exception as e:
        print("Error during audio pre-processing:", e)
        return input_file  # Fallback to original file if processing fails

def refine_srt_with_aeneas(audio_path, transcript_path, output_path, language="eng"):
    """
    Uses Aeneas to align transcript with audio and output an SRT.
    """
    config_string = "task_language=eng|os_task_file_format=srt|is_text_type=plain|is_text_type_unparsed=1|task_adjust_boundary_algorithm=percent|task_adjust_boundary_percent_value=15"

    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_path
    task.text_file_path_absolute = transcript_path
    task.sync_map_file_path_absolute = output_path

    ExecuteTask(task).execute()
    task.output_sync_map_file()
    print(f"Refined SRT written to {output_path}")

def srt_time_to_seconds(srt_time: str) -> float:
    """
    Convert an SRT timestamp ("HH:MM:SS,mmm") to seconds.
    Raises ValueError if the format is invalid.
    """
    if not _TIME_RE.match(srt_time):
        raise ValueError(f"Invalid SRT time: '{srt_time}'")
    h, m, rest = srt_time.split(":", 2)
    s, ms = rest.split(",", 1)
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def smooth_srt(subtitles, min_gap=0.1, min_duration=0.5):
    """
    Takes a list of {'start','end','text'} dicts and:
      - Merges entries if the gap between them is < min_gap
      - Ensures no entry is shorter than min_duration
    Skips any entry whose start/end aren’t valid SRT timestamps.
    """
    smoothed = []
    prev = None
    prev_start = prev_end = None

    for curr in subtitles:
        # Validate and parse current times
        try:
            cur_start = srt_time_to_seconds(curr['start'])
            cur_end   = srt_time_to_seconds(curr['end'])
        except Exception:
            # skip malformed entries
            continue

        if prev is None:
            prev = curr.copy()
            prev_start, prev_end = cur_start, cur_end
            continue

        gap = cur_start - prev_end
        if gap < min_gap:
            # merge into prev
            prev['end'] = curr['end']
            prev['text'] += " " + curr['text']
            prev_end = cur_end
        else:
            # finalize prev (ensure min_duration)
            dur = prev_end - prev_start
            if dur < min_duration:
                new_end = prev_start + min_duration
                prev['end'] = format_timestamp(new_end)
            smoothed.append(prev)

            # start new prev
            prev = curr.copy()
            prev_start, prev_end = cur_start, cur_end

    # final entry
    if prev is not None:
        dur = prev_end - prev_start
        if dur < min_duration:
            new_end = prev_start + min_duration
            prev['end'] = format_timestamp(new_end)
        smoothed.append(prev)

    return smoothed

def transcribe_with_whisperx(
    audio_path: str,
    model_name: str = "large",
    language: str = "en",
    #device: str = "cuda" if torch.cuda.is_available() else "cpu",
    device: str = "cpu",
    batch_size: int = 16,
    output_srt: str = "output/whisperx_transcript.srt",
    words_per_subtitle: int = 1,
) -> dict:
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

    print(f"[WhisperX] Loading Whisper model '{model_name}' on {device}…")
    model = whisperx.load_model(model_name, device="cpu",  compute_type="int8" if device == "cpu" else "float32")
    audio = whisperx.load_audio(audio_path)

    # 1. Transcribe with Whisper (this gives you segments + words but *un*-aligned)
    print(f"[WhisperX] Transcribing {audio_path} with model '{model_name}' on {device}…")

    # note: use whisperx.transcribe, not stable_whisper
    result = model.transcribe(
        audio,
        batch_size=batch_size,
        language=language,
        #word_timestamps=True
    )                                                                           # :contentReference[oaicite:2]{index=2}


    # 2. Load the alignment model and metadata
    print("[WhisperX] Loading alignment model…")
    align_model, metadata = whisperx.load_align_model(
        language_code=language or result["language"],
        device=device
    )

    # 3. Run forced alignment on the original audio + transcript
    print("[WhisperX] Running forced alignment…")
    result_aligned = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device=device,
        return_char_alignments=False
    )


    # <— Add this line so the writer can see the language
    result_aligned["language"] = result["language"]


    # 4. Export a word-level SRT directly on your *original* audio timestamps
    # TODO: the output file is named the same as the processed_audio (in future will change to same name for now this works fine)
    #? Note: the values are hardcoded for max_line_width/max_line_count for testing purporse (might change in the future)
    vtt_dir = os.path.dirname(output_srt) or "."
    os.makedirs(vtt_dir, exist_ok=True)
    print(f"[WhisperX] Writing WebVTT to {output_srt} via get_writer…")
    vtt_writer = get_writer("srt", vtt_dir)
    vtt_writer(
        result_aligned,
        audio_path,
        {
            "max_line_width": 5, #? the maximum number of characters in a line before breaking the lin
            "max_line_count": 1, #? the maximum number of lines in a segment
            "highlight_words": False #? underline each word as it is spoken in srt and vtt
        }
    )

    write_srt_n_words(
        aligned_result = result_aligned,
        audio_path = audio_path,
        output_srt = "output/whisperx_grouped.srt",
        words_per_subtitle = words_per_subtitle
    )


    print("[WhisperX] Done.")
    return result_aligned

def write_srt_n_words(
    aligned_result: Dict,
    audio_path: str,
    output_srt: str,
    words_per_subtitle: int,
    preserve_segments: bool = False
):
    """
    Write an SRT with exactly `words_per_subtitle` per cue,
    optionally ignoring original segments.
    """
    # 1) Flatten all words in time order
    all_words = []
    for seg in aligned_result["segments"]:
        for w in seg["words"]:
            all_words.append(w)

    # 2) Chunk and write
    os.makedirs(os.path.dirname(output_srt) or ".", exist_ok=True)
    with open(output_srt, "w", encoding="utf-8") as f:
        idx = 1
        for i in range(0, len(all_words), words_per_subtitle):
            chunk = all_words[i : i + words_per_subtitle]
            start = chunk[0]["start"]
            end   = chunk[-1]["end"]
            text  = " ".join(w["word"] for w in chunk).strip()
            f.write(f"{idx}\n")
            f.write(f"{_fmt_ts(start, always_include_hours=True, decimal_marker=',')} --> "
                    f"{_fmt_ts(end, always_include_hours=True, decimal_marker=',')}\n")
            f.write(text + "\n\n")
            idx += 1
    print(f"Wrote {idx-1} cues to {output_srt}")
