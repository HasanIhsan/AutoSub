# Auto Subs
> This project has been only tested on WSL Ubuntu
> I don't know if it works on windows (mainly because of SOX and other libs)
> but it should work fine

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/HasanIhsan/AutoSub)](https://github.com/HasanIhsan/AutoSub/issues)
[![GitHub stars](https://img.shields.io/github/stars/HasanIhsan/AutoSub)](https://github.com/HasanIhsan/AutoSub/stargazers)

## Description

AutoSubs is an automated subtitle generation tool that transforms audio content into precise SRT subtitle files. Key features:

🎙️ Multiple transcription engines (WhisperX, Stable-Whisper)

🔧 Audio preprocessing with noise reduction

⚙️ Adjustable subtitle parameters (words per subtitle, model sizes)
✏️ Subtitle timeline editor with live preview
🚀 Batch processing for long audio files (chunked processing)

Perfect for content creators, translators, and video producers needing accurate, customizable subtitles.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Installation

Prerequisites
Python 3.9+
FFmpeg
SoX (Sound eXchange)
NVIDIA GPU (recommended for GPU acceleration) (project currently uses CPU ONLY)

```bash
# Clone repository
$ git clone https://github.com/username/autosubs.git
$ cd autosubs

# Install dependencies
$ pip install -r requirements.txt

# Additional system packages (Ubuntu/Debian)
$ sudo apt install ffmpeg sox
```
> Note: I Switched To WSL Ubuntu (I might later remove SOX but for now read [sox on windows](https://stackoverflow.com/questions/17667491/how-to-use-sox-in-windows)

## Usage
1. Launch Application

```bash
$ python main_window.py
```
![main](https://github.com/user-attachments/assets/e447fb88-e34e-4873-9ba4-8fb7a4967daa)

2. Load Audio File
- Click "Add Audio Input" to select WAV file
- Supported formats: 16-bit WAV (auto-converted during processing)
- ![audio input](https://github.com/user-attachments/assets/c43b1398-e6e9-4b06-9be2-6b3f2c1d3350)

4. Configure Settings
- Transcriber: Choose between WhisperX/ (fast) or Stable-Whisper (accurate)/ whisperx_chuncked (for cpu)
- Model Size: Balance between speed and accuracy (tiny <-> large-v3)
- Language: Support for 50+ languages with auto-detection
- Words/Subtitle: Control subtitle density (1-10 words per line)
- ![settings](https://github.com/user-attachments/assets/023c490e-0a75-477d-9b43-b3b031cfae68)

5. Process Audio
- Click "Start Process" to begin transcription
- Progress shown in console output
- Processed files saved in /output directory
- ![console1](https://github.com/user-attachments/assets/a8307ea7-6318-4e87-a5a8-c0d069a689c0)

6. Edit & Preview
- Adjust subtitle timings in timeline view
- Edit text directly in timeline entries
- Preview synchronization with audio player
- ![preiview](https://github.com/user-attachments/assets/a6983be6-50e8-4371-bc2e-95238ad08135)
> the priview screen will be updated/fixed at a later date
> the SRT preivew doesn't work yet


## License
This project is licensed under the MIT License(LICENSE) 

## Credits
Maintainers: ME
