from PyQt5.QtCore import QSize, Qt, QObject, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QPushButton, \
    QToolButton, QSizePolicy, QApplication

from DataLogging.DataLoggingWindowUI import DataLoggingWindowUI
from MapDisplay.MapDisplayWindowUI import MapDisplayWindow, MapDisplayWindowUI
from PidTuning.PidTuningWindowUI import PidTuningWindowUI

from MainWindow.DroneVisualisation import DroneVisualisationUI
from MainWindow.VehicleCondition import VehicleConditionUI
from MainWindow.VehicleDirection import VehicleDirectionUI


class MainWindow:
    def __init__(self, view: "MainWindowUI"):
        self._view = view
        self.map_display_window_controller = MapDisplayWindow(view=self._view.map_display_window, model=None)

        self._connect_window_buttons()

    def _connect_window_buttons(self):
        self._view.map_button.clicked.connect(
            lambda checked: self._toggle_window(self._view.map_display_window, checked)
        )

        self._view.map_display_window.window_closed_signal.connect(
            lambda : self._view.set_map_button_checked(False),
        )

        self._view.pid_tuning_button.clicked.connect(
            lambda checked: self._toggle_window(self._view.pid_tuning_window, checked)
        )

        self._view.data_logging_button.clicked.connect(
            lambda checked: self._toggle_window(self._view.data_logging_window, checked)
        )

    @staticmethod
    def _toggle_window(window, state):
        if state:
            window.show()

        else:
            window.hide()


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

        self.map_button = QToolButton()
        self.map_button.setCheckable(True)
        self.map_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.map_button.setText("Map")
        self.map_button.setIcon(QIcon(":/image-placeholder.png"))
        self.map_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.map_button.setIconSize(QSize(90, 90))

        self.pid_tuning_button = QToolButton()
        self.pid_tuning_button.setCheckable(True)
        self.pid_tuning_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.pid_tuning_button.setText("PID tuning")
        self.pid_tuning_button.setIcon(QIcon(":/image-placeholder.png"))
        self.pid_tuning_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.pid_tuning_button.setIconSize(QSize(90, 90))

        self.data_logging_button = QToolButton()
        self.data_logging_button.setCheckable(True)
        self.data_logging_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.data_logging_button.setText("Data logging")
        self.data_logging_button.setIcon(QIcon(":/image-placeholder.png"))
        self.data_logging_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.data_logging_button.setIconSize(QSize(90, 90))

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

        self.data_logging_window = DataLoggingWindowUI()
        self.pid_tuning_window = PidTuningWindowUI()
        self.map_display_window = MapDisplayWindowUI()


    @pyqtSlot(bool)
    def set_map_button_checked(self, checked):
        self.map_button.setChecked(checked)


    def closeEvent(self, event):
        event.ignore()

        self.data_logging_window.close()
        self.map_display_window.close()
        self.pid_tuning_window.close()

        super().closeEvent(event)
