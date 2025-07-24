import sys

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QGridLayout, QLabel, QGroupBox, \
    QVBoxLayout, QProgressBar
from VehicleStatus import VehicleStatus, FlightMode
from DroneVisualisationWindow import DroneVisualisationWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QMainWindow {background-color: rgb(255,255,255);}")

        widget = QWidget()
        self.main_layout = QGridLayout()

        palette = self.palette()

        vehicle_condition_widget = UIVehicleCondition()
        self.main_layout.addWidget(vehicle_condition_widget, 0, 0)

        drone_visualisation_widget = UIDroneVisualisation()
        self.main_layout.addWidget(drone_visualisation_widget, 0, 1)

        vehicle_direction_widget = UIVehicleDirection()
        self.main_layout.addWidget(vehicle_direction_widget, 1, 0, 1, 2)

        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        self.setMinimumSize(QSize(640, 480))


class UIDroneVisualisation(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox {
                border: none;
            }
        """)
        self.layout = QGridLayout()

        self.drone_visualisation_window = DroneVisualisationWindow()
        self.drone_visualisation_widget = QWidget().createWindowContainer(self.drone_visualisation_window)

        self.layout.addWidget(self.drone_visualisation_widget, 0, 0)

        self.setLayout(self.layout)


class UIVehicleCondition(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox { 
                border: 2px solid gray; 
                border-color: rgba(200,200,200, 1); 
                font-size: 14px; 
                border-radius: 15px; 
                margin: 2px;
                margin-top: 10px;
                position: relative;
            }
            QGroupBox::title {
                background-color: white;
                position: absolute;
                top: -10px;
                left: 15px;
                padding-left:4px;
                padding-right:4px;
            }
        """)
        self.setTitle("General Information")
        self.layout = QVBoxLayout()

        # ---
        self.heartbeat = False
        self.heartbeat_widget = QWidget()
        self.heartbeat_layout = QHBoxLayout()
        self.heartbeat_widget.setLayout(self.heartbeat_layout)
        self.heartbeat_title = QLabel("Heartbeat")
        self.heartbeat_label = QLabel("ON" if self.heartbeat else "OFF")
        self.heartbeat_layout.addWidget(self.heartbeat_title)
        self.heartbeat_layout.addWidget(self.heartbeat_label)
        self.layout.addWidget(self.heartbeat_widget)

        # ---
        self.in_air = False
        self.in_air_widget = QWidget()
        self.in_air_layout = QHBoxLayout()
        self.in_air_widget.setLayout(self.in_air_layout)
        self.in_air_title = QLabel("In Air?")
        self.in_air_label = QLabel("YES" if self.in_air else "NO")
        self.in_air_layout.addWidget(self.in_air_title)
        self.in_air_layout.addWidget(self.in_air_label)
        self.layout.addWidget(self.in_air_widget)

        # ---
        self.battery_voltage = 0
        self.battery_percentage = 0
        self.battery_widget = QWidget()
        self.battery_layout = QHBoxLayout()
        self.battery_widget.setLayout(self.battery_layout)
        # ------
        self.battery_voltage_widget = QWidget()
        self.battery_voltage_layout = QVBoxLayout()
        self.battery_voltage_widget.setLayout(self.battery_voltage_layout)
        self.battery_voltage_title = QLabel("Battery Voltage")
        self.battery_voltage_layout.addWidget(self.battery_voltage_title)
        self.battery_voltage_label = QLabel(f"{self.battery_voltage:.2f} V")
        self.battery_voltage_layout.addWidget(self.battery_voltage_label)
        self.battery_layout.addWidget(self.battery_voltage_widget)
        # ------
        self.battery_percentage_widget = QProgressBar()
        self.battery_percentage_widget.setGeometry(0, 0, 100, 10)
        self.battery_percentage_widget.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid grey;
                        border-radius: 0px;
                        text-align: center;
                    }

                    QProgressBar::chunk {
                        background-color: #3add36;
                        width: 1px;
                    }
                """)
        self.battery_percentage_widget.setValue(10)
        self.battery_layout.addWidget(self.battery_percentage_widget)
        self.layout.addWidget(self.battery_widget)

        self.setLayout(self.layout)


class UIVehicleDirection(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox { 
                border: 2px solid gray; 
                border-color: rgba(200,200,200, 1); 
                font-size: 14px; 
                border-radius: 15px; 
                margin: 2px;
                margin-top: 10px;
                position: relative;
            }
            QGroupBox::title {
                background-color: white;
                position: absolute;
                top: -10px;
                left: 15px;
                padding-left:4px;
                padding-right:4px;
            }
        """)
        self.setTitle("Vehicle Direction")
        layout = QGridLayout()
        layout.addWidget(QLabel('--TESTING--'), 0, 0)
        self.setLayout(layout)


if __name__ == "__main__":
    vehicle_status = VehicleStatus()

    app = QApplication(sys.argv)
    view = MainWindow()
    view.show()
    sys.exit(app.exec())
