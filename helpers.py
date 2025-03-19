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

def refine_srt_with_gentle(audio_path, transcript_path, output_srt_path, language="eng"):
    """
    Refine SRT timings using the Gentle forced aligner.
    Assumes that Gentle is running locally (e.g., at http://localhost:8765).
    
    This function sends the audio and transcript to Gentle's API,
    then processes the JSON response to produce an SRT file.
    
    Note: Gentle's response format may vary; this is a simple example that
    creates an SRT with one entry per aligned word. (3/18/25)
    """
    import requests

    try:
        # Read the transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        # Gentle expects files; send the audio file as binary and transcript as form data.
        files = {
            "audio": open(audio_path, "rb"),
        }
        data = {
            "transcript": transcript
        }
        # Send request to Gentle's synchronous API
        response = requests.post("http://localhost:8765/transcriptions?async=false", files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            # Gentle returns a JSON object with an array of words.
            # We'll create an SRT with one entry per word.
            srt_index = 1
            with open(output_srt_path, "w", encoding="utf-8") as f_out:
                for word in result.get("words", []):
                    # Only process words with a valid alignment
                    if "start" in word and "end" in word and "alignedWord" in word:
                        start = float(word["start"])
                        end = float(word["end"])
                        text = word["alignedWord"] or ""
                        start_str = format_timestamp(start)
                        end_str = format_timestamp(end)
                        f_out.write(f"{srt_index}\n")
                        f_out.write(f"{start_str} --> {end_str}\n")
                        f_out.write(f"{text}\n\n")
                        srt_index += 1
            print(f"Refined SRT saved to {output_srt_path}")
        else:
            print("Error in Gentle alignment:", response.text)
    except Exception as e:
        print("Exception during forced alignment with Gentle:", e)
