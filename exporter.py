from helpers import format_timestamp

class Exporter:
    @staticmethod
    def save_transcription(transcription, output_file, words_per_subtitle=1):
        """
        Save the transcribed text to a file with a specified number of words per subtitle.
        
        Parameters:
          - transcription: The transcription result from Whisper.
          - output_file: The file path where the transcription will be saved.
          - words_per_subtitle: Number of words to group per line.
            For example, 3 will output 3 words per subtitle (line).
        """
        text = transcription["text"]
        
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
    def export_srt(transcription, output_srt_file, words_per_subtitle):
        """
        Export the transcription segments as an SRT file with a specified number 
        of words per subtitle. For each segment, splits the text into groups and
        divides the segment's time range evenly across those groups.
        
        Parameters:
          - transcription: The transcription result from Whisper (with 'segments').
          - output_srt_file: The file path where the SRT file will be saved.
          - words_per_subtitle: Number of words per subtitle line.
        """
        segments = transcription.get("segments", [])
        srt_index = 1
        with open(output_srt_file, "w", encoding="utf-8") as f:
            for segment in segments:
                seg_start = segment["start"]
                seg_end = segment["end"]
                seg_text = segment["text"].strip()
                if not seg_text:
                    continue
                words = seg_text.split()
                # Calculate the number of groups (subtitles) in this segment.
                n_groups = (len(words) + words_per_subtitle - 1) // words_per_subtitle
                if n_groups == 0:
                    continue
                # Divide the segment's duration evenly among groups.
                group_duration = (seg_end - seg_start) / n_groups
                for i in range(n_groups):
                    group_words = words[i*words_per_subtitle:(i+1)*words_per_subtitle]
                    group_text = " ".join(group_words)
                    group_start = seg_start + i * group_duration
                    group_end = seg_start + (i+1) * group_duration
                    start_str = format_timestamp(group_start)
                    end_str = format_timestamp(group_end)
                    f.write(f"{srt_index}\n")
                    f.write(f"{start_str} --> {end_str}\n")
                    f.write(f"{group_text}\n\n")
                    srt_index += 1
        print(f"SRT file saved to {output_srt_file}")
