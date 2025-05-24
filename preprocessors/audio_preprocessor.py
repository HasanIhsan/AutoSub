import subprocess
from pydub import AudioSegment
from pathlib import Path

class AudioPreprocessor:
    def __init__(self, noise_sec: float = 0.5):
        self.noise_sec = noise_sec

    def process(self, input_file: str, output_file: str) -> str:
        """
            Pre-process the audio file by converting it to mono and normalizing its volume.
            Requires pydub. (3/18/25)
        """
        
        normalized = None
        try:
            
            # Make sure output directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)


            # 1) Load & normalize with Pydub
            audio = AudioSegment.from_file(input_file, format="wav")
            audio = audio.set_channels(1)
            # target -20 dBFS
            change_in_dBFS = -20.0 - audio.dBFS
            normalized = audio.apply_gain(change_in_dBFS)

            # 2) Write out a temp WAV
            temp_wav = "output/temp_for_noise.wav"
            normalized.export(temp_wav, format="wav")

            # 3) Create a noise profile from the first 0.5s
            noise_prof = "output/noise.prof"
            subprocess.run([
                "sox", temp_wav, "-n",
                "trim", "0", "0.5",      # take first half-second as “noise”
                "noiseprof", noise_prof
            ], check=True)

            # 4) Apply noise reduction to the entire file
            subprocess.run([
                "sox", temp_wav, output_file,
                "noisered", noise_prof
            ], check=True)

            print(f"Pre-processed audio (noise-reduced via SoX) saved to {output_file}")
            return output_file

        except Exception as e:
            print("Error during audio pre-processing:", e)
            # Fallback: return the normalized version
            try:
                if normalized is not None:
                    normalized.export(output_file, format="wav")
                    print(f"Exported normalized audio (no noise reduction) to {output_file}")
                    return output_file
                else:
                    print(f"Using original input file as fallback: {input_file}")
                    return input_file
                
            except:
                return input_file