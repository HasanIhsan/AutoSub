import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QComboBox, QScrollArea, QLineEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from controller import AutoSubsController  # Import the controller

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoSubs UI")
        self.setGeometry(100, 100, 1200, 800)

        # Main container widget & layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.left_panel = self.create_left_panel()  # For timeline updates
        right_panel = self.create_right_panel()

        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        self.setCentralWidget(main_widget)

        # List to hold subtitle row references (each is a dict with 'start', 'end', 'edit')
        self.subtitle_rows = []

        # Create controller instance
        self.controller = AutoSubsController(self)

    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        title_label = QLabel("Generate Subtitles")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)

        # Scrollable timeline area
        self.timeline_area = QScrollArea()
        self.timeline_area.setWidgetResizable(True)
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setSpacing(5)
        self.timeline_area.setWidget(self.timeline_container)

        bottom_button_layout = QHBoxLayout()
        self.reexport_button = QPushButton("Re-Export")
        bottom_button_layout.addWidget(self.reexport_button)
        bottom_button_layout.addStretch()

        left_layout.addWidget(title_label)
        left_layout.addWidget(self.timeline_area)
        left_layout.addLayout(bottom_button_layout)

        return left_widget

    def update_timeline(self, subtitles):
        """
        Update the timeline area with subtitles.
        Each row contains a label (with time) and an editable text box.
        """
        # Clear existing items and list
        self.subtitle_rows = []
        for i in reversed(range(self.timeline_layout.count())):
            widget_to_remove = self.timeline_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Add each subtitle as a row
        for sub in subtitles:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 5, 5, 5)

            time_label = QLabel(f"{sub['start']} --> {sub['end']}")
            time_label.setFixedWidth(150)
            subtitle_edit = QLineEdit(sub['text'])
            # Make editable (remove readOnly)
            subtitle_edit.setReadOnly(False)

            row_layout.addWidget(time_label)
            row_layout.addWidget(subtitle_edit)
            self.timeline_layout.addWidget(row_widget)

            # Store row info so controller can read updated text later
            self.subtitle_rows.append({
                "start": sub["start"],
                "end": sub["end"],
                "edit": subtitle_edit
            })

        self.timeline_container.adjustSize()

    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        flow_title = QLabel("Transcription Flow")
        flow_title_font = QFont("Arial", 16, QFont.Bold)
        flow_title.setFont(flow_title_font)

        # Container for the steps
        steps_container = QWidget()
        steps_layout = QVBoxLayout(steps_container)
        steps_layout.setSpacing(20)

        # Process Settings
        step1_group = QGroupBox("Process Settings")
        step1_layout = QVBoxLayout(step1_group)
        self.start_process_button = QPushButton("Start Process")
        step1_layout.addWidget(self.start_process_button)

        # Audio Source
        step3_group = QGroupBox("Audio Source")
        step3_layout = QVBoxLayout(step3_group)
        self.audio_source_button = QPushButton("Add Audio Input")
        self.audio_file_label = QLabel("No file selected")
        step3_layout.addWidget(self.audio_source_button)
        step3_layout.addWidget(self.audio_file_label)

        # Transcribe Settings
        step4_group = QGroupBox("Transcribe Settings")
        step4_layout = QVBoxLayout(step4_group)
        language_label = QLabel("Select Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "French", "Spanish", "German", "Italian", "Portuguese", "Detect"])
        model_label = QLabel("Select Model Size:")
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItems(["tiny", "small", "medium", "large"])
        words_label = QLabel("Words per Subtitle:")
        self.words_per_subtitle_edit = QLineEdit("1")
        
        step4_layout.addWidget(language_label)
        step4_layout.addWidget(self.language_combo)
        step4_layout.addWidget(model_label)
        step4_layout.addWidget(self.model_size_combo)
        step4_layout.addWidget(words_label)
        step4_layout.addWidget(self.words_per_subtitle_edit)

        steps_layout.addWidget(step1_group)
        steps_layout.addWidget(step3_group)
        steps_layout.addWidget(step4_group)
        steps_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(steps_container)

        right_layout.addWidget(flow_title)
        right_layout.addWidget(scroll_area)

        return right_widget

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
