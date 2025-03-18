import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QComboBox, QScrollArea, QFrame, QRadioButton
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Basic window properties
        self.setWindowTitle("AutoSubs UI")
        self.setGeometry(100, 100, 1200, 800)

        # Main container widget & layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Create left (sidebar) and right (main content) panels
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        # Add panels to the main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        self.setCentralWidget(main_widget)

    def create_left_panel(self):
        """
        Creates the left sidebar panel with:
        - "Generate Subtitles" title
        - "Support AutoSubs" & "GitHub" buttons at the top
        - Large area with "No subtitles found..." text
        - "Refresh" & "Export" buttons at the bottom
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        # Title: "Generate Subtitles"
        title_label = QLabel("Generate Subtitles")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)

        # Row of buttons at the top: "Support AutoSubs" and "GitHub"
        top_button_layout = QHBoxLayout()
        #support_button = QPushButton("Support AutoSubs")
        #github_button = QPushButton("GitHub")
        #top_button_layout.addWidget(support_button)
        #top_button_layout.addWidget(github_button)
        top_button_layout.addStretch()  # push them to the left

        # Large label in the center: "No subtitles found for this timeline"
        timeline_label = QLabel("No subtitles found for this timeline")
        timeline_label.setAlignment(Qt.AlignCenter)
        timeline_label.setStyleSheet("font-size: 14px; color: #777;")

        # Row of buttons at the bottom: "Refresh" and "Export"
        bottom_button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        #export_button = QPushButton("Export")
        bottom_button_layout.addWidget(refresh_button)
        #bottom_button_layout.addWidget(export_button)
        bottom_button_layout.addStretch()

        # Assemble left layout
        left_layout.addWidget(title_label)
        left_layout.addLayout(top_button_layout)
        left_layout.addStretch()  # push content to top and bottom
        left_layout.addWidget(timeline_label)
        left_layout.addStretch()
        left_layout.addLayout(bottom_button_layout)

        return left_widget

    def create_right_panel(self):
        """
        Creates the right main panel with:
        - "Transcription Flow" title
        - Steps: Select Template, Stack subtitles, Video track, Start Process, etc.
        - Scroll area to hold all steps
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # Title: "Transcription Flow"
        flow_title = QLabel("Transcription Flow")
        flow_title_font = QFont("Arial", 16, QFont.Bold)
        flow_title.setFont(flow_title_font)

        # A container for all steps (so we can put it in a scroll area)
        steps_container = QWidget()
        steps_layout = QVBoxLayout(steps_container)
        steps_layout.setSpacing(20)

        #
        # STEP 1: (GroupBox) "Select Template", "Stack for more subtitles", etc.
        #
        step1_group = QGroupBox("Select Template & Video")
        step1_layout = QVBoxLayout(step1_group)
        step1_layout.setSpacing(10)

        #label_select_template = QLabel("Select Template:")
        #combo_template = QComboBox()
        #combo_template.addItems(["Template 1", "Template 2"])

        #label_stack_subtitles = QLabel("Stack for more subtitles?")
        #combo_stack = QComboBox()
        #combo_stack.addItems(["No", "Yes"])

        #label_select_video = QLabel("Select Video Track:")
        #combo_video = QComboBox()
        #combo_video.addItems(["Track 1", "Track 2"])

        start_button = QPushButton("Start Process")

        #step1_layout.addWidget(label_select_template)
        #step1_layout.addWidget(combo_template)
        #step1_layout.addWidget(label_stack_subtitles)
        #step1_layout.addWidget(combo_stack)
        #step1_layout.addWidget(label_select_video)
        #step1_layout.addWidget(combo_video)
        step1_layout.addWidget(start_button)

     

        #
        # STEP 3: (GroupBox) "Audio Source"
        #
        step3_group = QGroupBox("Audio Source")
        step3_layout = QVBoxLayout(step3_group)
        step3_layout.setSpacing(10)

        step3_button = QPushButton("Add Audio Input")
    
 
        step3_layout.addWidget(step3_button)

        #
        # STEP 4: (GroupBox) "Transcribe"
        #
        step4_group = QGroupBox("Transcribe")
        step4_layout = QVBoxLayout(step4_group)
        step4_layout.setSpacing(10)

        label_transcribe_model = QLabel("Use Whisper Large")
        label_language = QLabel("Language: English -> English")
        label_oneWord = QLabel("1 Word SubTitles?")
        step4_radioBtn = QRadioButton()

        step4_layout.addWidget(label_transcribe_model)
        step4_layout.addWidget(label_language)
 

        #
        # Add everything to the steps layout
        #
        steps_layout.addWidget(step1_group) 
        steps_layout.addWidget(step3_group)
        steps_layout.addWidget(step4_group) 
        steps_layout.addStretch()

        # Make the steps scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(steps_container)

        # Add to right panel layout
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
