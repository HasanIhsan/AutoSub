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

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        self.setCentralWidget(main_widget)

        # Create the controller and pass this UI instance to it.
        self.controller = AutoSubsController(self)

    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        title_label = QLabel("Generate Subtitles")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)

        top_button_layout = QHBoxLayout()
        top_button_layout.addStretch()

        timeline_label = QLabel("No subtitles found for this timeline")
        timeline_label.setAlignment(Qt.AlignCenter)
        timeline_label.setStyleSheet("font-size: 14px; color: #777;")

        bottom_button_layout = QHBoxLayout()
        reExport_button = QPushButton("Re-Export")
        bottom_button_layout.addWidget(reExport_button)
        bottom_button_layout.addStretch()

        left_layout.addWidget(title_label)
        left_layout.addLayout(top_button_layout)
        left_layout.addStretch()
        left_layout.addWidget(timeline_label)
        left_layout.addStretch()
        left_layout.addLayout(bottom_button_layout)

        return left_widget

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

        # STEP 1: Process Settings
        step1_group = QGroupBox("Process Settings")
        step1_layout = QVBoxLayout(step1_group)
        self.start_process_button = QPushButton("Start Process")
        step1_layout.addWidget(self.start_process_button)

        # STEP 2: Audio Source
        step3_group = QGroupBox("Audio Source")
        step3_layout = QVBoxLayout(step3_group)
        self.audio_source_button = QPushButton("Add Audio Input")
        self.audio_file_label = QLabel("No file selected")
        step3_layout.addWidget(self.audio_source_button)
        step3_layout.addWidget(self.audio_file_label)

        # STEP 3: Transcribe Settings
        step4_group = QGroupBox("Transcribe Settings")
        step4_layout = QVBoxLayout(step4_group)
        # Language dropdown
        language_label = QLabel("Select Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "French", "Spanish", "German", "Italian", "Portuguese", "Detect"])
        # Model size dropdown
        model_label = QLabel("Select Model Size:")
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItems(["tiny", "small", "medium", "large"])
        # Text box for words per subtitle
        words_label = QLabel("Words per Subtitle:")
        self.words_per_subtitle_edit = QLineEdit("1")
        
        step4_layout.addWidget(language_label)
        step4_layout.addWidget(self.language_combo)
        step4_layout.addWidget(model_label)
        step4_layout.addWidget(self.model_size_combo)
        step4_layout.addWidget(words_label)
        step4_layout.addWidget(self.words_per_subtitle_edit)

        # Assemble all groups into the steps layout
        steps_layout.addWidget(step1_group)
        steps_layout.addWidget(step3_group)
        steps_layout.addWidget(step4_group)
        steps_layout.addStretch()

        # Make the steps scrollable
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
