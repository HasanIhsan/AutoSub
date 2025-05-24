from utils.srt_utils import format_timestamp

class Exporter:
    @staticmethod
    def save_transcription(transcription, output_file, words_per_subtitle):
        """
        Save the transcribed text to a file with a specified number of words per subtitle.

        Parameters:
          - transcription: The transcription result from Whisper.
          - output_file: The file path where the transcription will be saved.
          - words_per_subtitle: Number of words to group per line.
            For example, 3 will output 3 words per subtitle (line).(3/13/25)
        """
        text = transcription.text

        if words_per_subtitle > 0:
            words = text.split()
            lines = [
                " ".join(words[i:i+words_per_subtitle])
                for i in range(0, len(words), words_per_subtitle)
            ]
            text = "\n".join(lines)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Transcription saved to {output_file}")


    @staticmethod
    def export_srt(transcription, output_srt_file, words_per_subtitle, pause_thre):
        """
        Export the transcription segments as an SRT file with a specified number
        of words per subtitle. For each segment, splits the text into groups and
        divides the segment's time range evenly across those groups.

        Parameters:
          - transcription: The transcription result from Whisper (with 'segments').
          - output_srt_file: The file path where the SRT file will be saved.
          - words_per_subtitle: Number of words per subtitle line. (3/13/25)
        """
        """
        Export the transcription segments as an SRT file with improved timing accuracy.
        Uses the actual word-level timestamps and groups words based on words_per_subtitle. (3/14/25)

        Uses word-level timestamps and optionally groups words based on pause detection.(3/14/25)
        """
        def get_words(segment):
            if hasattr(segment, "words"):
                return segment.words
            elif isinstance(segment, dict):
                return segment.get("words", [])
            else:
                return []

        def get_val(item, key):
            if hasattr(item, key):
                return getattr(item, key)
            elif isinstance(item, dict):
                return item.get(key)
            else:
                raise AttributeError(f"Item has no attribute or key '{key}'.")

        # Fix for hybrid support: object or dict
        if hasattr(transcription, "segments"):
            segments = transcription.segments
        elif isinstance(transcription, dict):
            segments = transcription.get("segments", [])
        else:
            raise TypeError("transcription must be an object with a 'segments' attribute or a dict with a 'segments' key.")

        srt_index = 1

        with open(output_srt_file, "w", encoding="utf-8") as f:
            for segment in segments:
                words = get_words(segment)
                if not words:
                    print(f"Segment has no words: {segment}")
                    continue

                group_start = None
                group_end = None
                group_text = []
                prev_end = None

                for word in words:
                    start = get_val(word, "start")
                    end = get_val(word, "end")
                    text = get_val(word, "word")

                    if group_start is None:
                        group_start = start

                    if prev_end is not None and (start - prev_end) > pause_thre:
                        # Write current group
                        if group_text:
                            start_str = format_timestamp(group_start)
                            end_str = format_timestamp(prev_end)
                            f.write(f"{srt_index}\n")
                            f.write(f"{start_str} --> {end_str}\n")
                            f.write(f"{' '.join(group_text)}\n\n")
                            srt_index += 1
                            group_text = []
                            group_start = start

                    group_text.append(text)
                    group_end = end
                    prev_end = end

                    if len(group_text) >= words_per_subtitle:
                        start_str = format_timestamp(group_start)
                        end_str = format_timestamp(group_end)
                        f.write(f"{srt_index}\n")
                        f.write(f"{start_str} --> {end_str}\n")
                        f.write(f"{' '.join(group_text)}\n\n")
                        srt_index += 1
                        group_text = []
                        group_start = None

                if group_text:
                    start_str = format_timestamp(group_start)
                    end_str = format_timestamp(group_end)
                    f.write(f"{srt_index}\n")
                    f.write(f"{start_str} --> {end_str}\n")
                    f.write(f"{' '.join(group_text)}\n\n")
                    srt_index += 1

        print(f"SRT file saved to {output_srt_file}")

    @staticmethod
    def re_export_srt(subtitles, output_srt_file):
        """
        Re-export subtitles to an SRT file.
        'subtitles' is expected to be a list of dicts with keys 'start', 'end', 'text' (3/18/2025)
        """
        with open(output_srt_file, "w", encoding="utf-8") as f:
            for i, sub in enumerate(subtitles, start=1):
                f.write(f"{i}\n")
                f.write(f"{sub['start']} --> {sub['end']}\n")
                f.write(f"{sub['text']}\n\n")
        print(f"SRT file re-exported to {output_srt_file}")
