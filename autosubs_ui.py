import tkinter as tk
from tkinter import ttk, filedialog
from controller import AutoSubsController  # Import the controller

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AutoSubs UI")
        self.geometry("1200x800")

        # Main layout: 2 panels (left and right)
        self.left_panel = self.create_left_panel()  # For timeline updates
        self.right_panel = self.create_right_panel()

        self.left_panel.grid(row=0, column=0, sticky="nswe")
        self.right_panel.grid(row=0, column=1, sticky="nswe")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.subtitle_rows = []  # YYYY/MM/DD

        # Pass this window as UI to controller
        self.controller = AutoSubsController(self)

    def create_left_panel(self):
        frame = ttk.Frame(self, padding=10)
        ttk.Label(frame, text="Generate Subtitles", font=("Arial", 18, "bold")).pack(pady=(0, 10))

        self.timeline_container = tk.Canvas(frame)
        self.scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.timeline_container.yview)
        self.timeline_frame = ttk.Frame(self.timeline_container)

        self.timeline_frame.bind("<Configure>", lambda e: self.timeline_container.configure(scrollregion=self.timeline_container.bbox("all")))
        self.timeline_container.create_window((0, 0), window=self.timeline_frame, anchor="nw")
        self.timeline_container.configure(yscrollcommand=self.scrollbar.set)

        self.timeline_container.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        bottom_frame = ttk.Frame(frame)
        self.reexport_button = ttk.Button(bottom_frame, text="Re-Export")
        self.reexport_button.pack(side="left")
        bottom_frame.pack(fill="x", pady=(10, 0))

        return frame

    def create_right_panel(self):
        frame = ttk.Frame(self, padding=10)

        ttk.Label(frame, text="Transcription Flow", font=("Arial", 16, "bold")).pack(anchor="w")

        # Process Settings
        step1 = ttk.LabelFrame(frame, text="Process Settings", padding=10)
        self.start_process_button = ttk.Button(step1, text="Start Process")
        self.start_process_button.pack()
        step1.pack(fill="x", pady=10)

        # Audio Source
        step3 = ttk.LabelFrame(frame, text="Audio Source", padding=10)
        self.audio_source_button = ttk.Button(step3, text="Add Audio Input")
        self.audio_file_label = ttk.Label(step3, text="No file selected")
        self.audio_source_button.pack()
        self.audio_file_label.pack()
        step3.pack(fill="x", pady=10)

        # Transcribe Settings
        step4 = ttk.LabelFrame(frame, text="Transcribe Settings", padding=10)
        ttk.Label(step4, text="Select Language:").pack(anchor="w")
        self.language_combo = ttk.Combobox(step4, values=["English", "French", "Spanish", "German", "Italian", "Portuguese", "Detect"])
        self.language_combo.set("English")
        self.language_combo.pack(fill="x")

        ttk.Label(step4, text="Select Model Size:").pack(anchor="w", pady=(10, 0))
        self.model_size_combo = ttk.Combobox(step4, values=["tiny", "small", "medium", "large"])
        self.model_size_combo.set("tiny")
        self.model_size_combo.pack(fill="x")

        ttk.Label(step4, text="Words per Subtitle:").pack(anchor="w", pady=(10, 0))
        self.words_per_subtitle_edit = ttk.Entry(step4)
        self.words_per_subtitle_edit.insert(0, "1")
        self.words_per_subtitle_edit.pack(fill="x")

        step4.pack(fill="x", pady=10)

        return frame

    def update_timeline(self, subtitles):
        # YYYY/MM/DD: clear old rows
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()
        self.subtitle_rows = []

        for sub in subtitles:
            row = ttk.Frame(self.timeline_frame, padding=5)
            ttk.Label(row, text=f"{sub['start']} --> {sub['end']}", width=20).pack(side="left")
            entry = ttk.Entry(row)
            entry.insert(0, sub['text'])
            entry.pack(side="left", fill="x", expand=True)
            row.pack(fill="x")

            self.subtitle_rows.append({
                "start": sub["start"],
                "end": sub["end"],
                "edit": entry
            })

    def close(self):
        # YYYY/MM/DD: ensure Gentle is stopped on exit
        self.controller.stop_gentle()
        self.destroy()

def main():
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.close)
    app.mainloop()

if __name__ == "__main__":
    main()
