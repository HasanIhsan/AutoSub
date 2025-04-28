import tkinter as tk
from tkinter import ttk, filedialog
import pygame

from helpers import read_srt, format_timestamp

class PreviewWindow(tk.Toplevel):
    def __init__(self, master, audio_path, srt_path):
        super().__init__(master)
        self.title("Audio Preview")
        self.geometry("600x300")
        self.audio_path = audio_path

        # Load subtitles
        self.sub_entries = []  # list of (start_sec, end_sec, text)
        if srt_path:
            raw = read_srt(srt_path)
            self.sub_entries = []
            for ent in raw:
                start = self._parse_ts(ent['start'])
                end = self._parse_ts(ent['end'])
                self.sub_entries.append((start, end, ent['text']))

        # Pre-init pygame mixer
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=4096)
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_path)
        sound = pygame.mixer.Sound(self.audio_path)
        self.duration = sound.get_length()
        self.start_offset = 0.0

        # Subtitle display
        self.subtitle_label = ttk.Label(self, text="", wraplength=580, anchor="center", font=("Arial", 12))
        self.subtitle_label.pack(pady=(10, 0))

        # Tick canvas
        self.tick_canvas = tk.Canvas(self, height=20)
        self.tick_canvas.pack(fill="x", padx=10)
        self._draw_ticks()

        # Progress bar scale
        self.progress = ttk.Scale(self, from_=0, to=self.duration, orient="horizontal")
        self.progress.pack(fill="x", padx=10, pady=(0,10))
        self.progress.bind("<ButtonRelease-1>", lambda e: self.on_seek())

        # Play/Stop buttons
        btn_frame = ttk.Frame(self)
        self.play_btn = ttk.Button(btn_frame, text="Play", command=self.play)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop)
        self.play_btn.pack(side="left", padx=5)
        self.stop_btn.pack(side="left", padx=5)
        btn_frame.pack(pady=5)

        self._updating = False

    def _parse_ts(self, ts_str):
        # "HH:MM:SS,mmm" -> seconds
        h, m, rest = ts_str.split(":")
        s, ms = rest.split(",")
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

    def _draw_ticks(self):
        w = self.tick_canvas.winfo_reqwidth() or 580
        for start, _, _ in self.sub_entries:
            x = int((start/self.duration) * w)
            self.tick_canvas.create_line(x, 0, x, 20)

    def play(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.start_offset = self.progress.get()
        pygame.mixer.music.play(loops=0, start=self.start_offset)
        if not self._updating:
            self._updating = True
            self.update_progress()

    def stop(self):
        pygame.mixer.music.stop()
        self._updating = False

    def update_progress(self):
        if pygame.mixer.music.get_busy():
            elapsed = pygame.mixer.music.get_pos() / 1000.0
            pos = self.start_offset + elapsed
            self.progress.set(min(pos, self.duration))
            self._update_subtitle(pos)
            self.after(200, self.update_progress)
        else:
            self._updating = False

    def on_seek(self):
        self.start_offset = float(self.progress.get())
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.play(loops=0, start=self.start_offset)
        self._update_subtitle(self.start_offset)

    def _update_subtitle(self, current_time):
        # Find matching subtitle
        text = ''
        for start, end, txt in self.sub_entries:
            if start <= current_time <= end:
                text = txt
                break
        self.subtitle_label.config(text=text)
