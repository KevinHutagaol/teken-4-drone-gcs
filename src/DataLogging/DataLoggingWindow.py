from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class DataLoggingWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("--- Data Logging ---")
        layout.addWidget(self.label)
        self.setLayout(layout)