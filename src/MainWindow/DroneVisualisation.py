from PyQt5.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel

from src.MainWindow.DroneVisualisation3DWindow import DroneVisualisation3DWindow


class DroneVisualisationUI(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox {
                border: none;
            }
        """)
        self.layout = QGridLayout()

        self.drone_visualisation_window = DroneVisualisation3DWindow()
        self.drone_visualisation_widget = QWidget().createWindowContainer(self.drone_visualisation_window)

        self.layout.addWidget(self.drone_visualisation_widget, 0, 0)

        self.setLayout(self.layout)