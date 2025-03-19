
import subprocess
import time
import requests

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

def refine_srt_with_gentle(audio_path, transcript_path, output_srt_path, language="eng", words_per_subtitle=1):
    """
    Refine SRT timings using the Gentle forced aligner, grouping the aligned words
    into subtitles based on the given words_per_subtitle.
    
    Assumes that Gentle is running locally (e.g., at http://localhost:8765).
    
    This function sends the audio and transcript to Gentle's API, then processes the 
    JSON response to produce an SRT file. The output is grouped by the specified word count.
    
    Parameters:
      - audio_path: Path to the audio file.
      - transcript_path: Path to the transcript text file.
      - output_srt_path: Path where the refined SRT will be saved.
      - language: (Optional) Language code for Gentle alignment (default "eng").
      - words_per_subtitle: Number of words per subtitle line.
    """
    import requests
    from helpers import format_timestamp

    try:
        # Read the transcript from file
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        # Gentle expects files; send the audio file as binary and transcript as form data.
        files = {"audio": open(audio_path, "rb")}
        data = {"transcript": transcript}
        # Send request to Gentle's synchronous API
        response = requests.post("http://localhost:8765/transcriptions?async=false", files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            # Filter out words that don't have "start" or "end" values.
            raw_words = result.get("words", [])
            words = [w for w in raw_words if "start" in w and "end" in w]
            srt_index = 1
            with open(output_srt_path, "w", encoding="utf-8") as f_out:
                # Group words into chunks of words_per_subtitle
                for i in range(0, len(words), words_per_subtitle):
                    group = words[i:i+words_per_subtitle]
                    if not group:
                        continue
                    group_start = float(group[0]["start"])
                    group_end = float(group[-1]["end"])
                    # Join the aligned words (use .strip() to remove unwanted spaces)
                    group_text = " ".join(word.get("alignedWord", "").strip() for word in group)
                    start_str = format_timestamp(group_start)
                    end_str = format_timestamp(group_end)
                    f_out.write(f"{srt_index}\n")
                    f_out.write(f"{start_str} --> {end_str}\n")
                    f_out.write(f"{group_text}\n\n")
                    srt_index += 1
            print(f"Refined SRT saved to {output_srt_path}")
        else:
            print("Error in Gentle alignment:", response.text)
    except Exception as e:
        print("Exception during forced alignment with Gentle:", e)

 

def docker_gentle_process(timeout=60):
    """
    Launch Gentle in Docker using PowerShell and poll its endpoint until it is ready.
    
    This function runs the docker command to launch Gentle, explicitly mapping port 8765,
    and then repeatedly polls http://localhost:8765 until it responds or times out.
    
    Parameters:
      timeout (int): Maximum seconds to wait before timing out.
    
    Returns:
      process: The subprocess.Popen object representing the Docker process.
    
    Raises:
      Exception: If the server does not start within the timeout.
    """
    # Use -p 8765:8765 to ensure the host port is fixed.
    command = "docker run -p 8765:8765 lowerquality/gentle"
    proc = subprocess.Popen(
        ["powershell", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    start_time = time.time()
    url = "http://localhost:8765"
    while True:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("Gentle is now running via Docker.")
                break
        except Exception:
            pass  # ignore connection errors until Gentle is up
        if time.time() - start_time > timeout:
            proc.kill()
            raise Exception("Timeout waiting for Gentle Docker container to start.")
        time.sleep(0.5)
    return proc