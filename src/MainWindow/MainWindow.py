from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QPushButton

from src.MainWindow.DroneVisualisation import DroneVisualisationUI
from src.MainWindow.VehicleCondition import VehicleConditionUI
from src.MainWindow.VehicleDirection import VehicleDirectionUI


class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("QMainWindow {background-color: rgb(255,255,255);}")

        self.body_widget = QWidget()
        self.body_layout = QHBoxLayout()

        self.body_layout.setContentsMargins(0, 0, 0, 0)

        # SIDEBAR

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("side-bar")
        self.sidebar_widget.setStyleSheet("""
            #side-bar {
                background-color: transparent;
                border-right: 2px solid rgba(0,0,0, 0.2);
            }
        """)
        self.sidebar_layout = QVBoxLayout()

        self.map_button = QPushButton("Map")
        self.map_button.setCheckable(True)
        self.pid_tuning_button = QPushButton("PID tuning")
        self.pid_tuning_button.setCheckable(True)
        self.data_logging_button = QPushButton("Data logging")
        self.data_logging_button.setCheckable(True)

        self.sidebar_layout.addWidget(self.map_button)
        self.sidebar_layout.addWidget(self.pid_tuning_button)
        self.sidebar_layout.addWidget(self.data_logging_button)

        self.sidebar_widget.setLayout(self.sidebar_layout)
        self.sidebar_widget.setFixedWidth(120)

        self.body_layout.addWidget(self.sidebar_widget)

        # MAIN

        self.main_widget = QWidget()
        self.main_layout = QGridLayout()

        self.vehicle_condition_widget = VehicleConditionUI()
        self.main_layout.addWidget(self.vehicle_condition_widget, 0, 0)

        self.drone_visualisation_widget = DroneVisualisationUI()
        self.main_layout.addWidget(self.drone_visualisation_widget, 0, 1)

        self.vehicle_direction_widget = VehicleDirectionUI()
        self.main_layout.addWidget(self.vehicle_direction_widget, 1, 0, 1, 2)

        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 1)

        self.main_widget.setLayout(self.main_layout)

        self.body_layout.addWidget(self.main_widget)

        # ---
        self.body_widget.setLayout(self.body_layout)

        self.setCentralWidget(self.body_widget)
        self.setMinimumSize(QSize(720, 480))  # 640 x 480 is microsoft recommendation

        # OTHER WINDOWS

    def toggle_window(self, window):
        if window.isVisible():
            window.hide()

        else:
            window.show()
