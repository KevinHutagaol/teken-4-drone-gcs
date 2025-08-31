from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QWidget, QLabel

from MainWindow.DroneVisualisation3DWindow import DroneVisualisation3DWindow, OrbitTransformController
from VehicleStatus import Attitude


class DroneVisualisation(QObject):
    def __init__(self, view: 'DroneVisualisationUI'):
        super().__init__()
        self._view = view

    def update_drone_3d_model(self, att: 'Attitude'):
        self._view.drone_visualisation_window.controller.setAttitude(att)


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