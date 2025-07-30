from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class MapDisplayWindow:
    pass

class MapDisplayWindowUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("--- Map Display ---")
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setMinimumSize(QSize(640, 480))
