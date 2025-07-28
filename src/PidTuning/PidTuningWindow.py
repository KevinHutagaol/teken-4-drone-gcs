from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class PidTuningWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("--- PID Tuning ---")
        layout.addWidget(self.label)
        self.setLayout(layout)