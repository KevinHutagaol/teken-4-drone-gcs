import os
import sys

from os import listdir
from os.path import isfile, join

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QFontDatabase
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QGridLayout, QLabel, QGroupBox, \
    QVBoxLayout, QProgressBar

from pymavlink import mavutil


from VehicleStatus import VehicleStatus, FlightMode, Position, Attitude
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

        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 1)

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
        self.drone_visualisation_widget = (QWidget()
                                           .createWindowContainer(self.drone_visualisation_window))

        self.layout.addWidget(self.drone_visualisation_widget, 0, 0)

        self.setLayout(self.layout)


class UIVehicleCondition(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox { 
                border: 2px solid rgba(200,200,200, 1);  
                font-size: 14px; 
                border-radius: 15px;
                margin: 2px;
                margin-top: 10px;
                position: relative;
            }
            QGroupBox::title {
                font-size: 18px;    
                background-color: white;
                position: absolute;
                top: -10px;
                left: 15px;
                padding-left:4px;
                padding-right:4px;
            }
            
            /* * {background-color: rgba(255,0,0, 0.2)} */
        """)
        self.setTitle("General Information")
        font_temp = self.font()
        font_temp.setBold(True)
        self.setFont(font_temp)

        self.layout = QVBoxLayout()

        # ---
        self.heartbeat = False
        self.heartbeat_widget = QWidget()
        self.heartbeat_layout = QHBoxLayout()
        self.heartbeat_widget.setLayout(self.heartbeat_layout)
        self.heartbeat_title = QLabel("Heartbeat")
        self.heartbeat_title.setFixedWidth(125)
        self.heartbeat_label = QLabel("ON" if self.heartbeat else "OFF")
        self.heartbeat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heartbeat_layout.addWidget(self.heartbeat_title)
        self.heartbeat_layout.addWidget(self.heartbeat_label)
        self.layout.addWidget(self.heartbeat_widget)

        # ---
        self.in_air = False
        self.in_air_widget = QWidget()
        self.in_air_layout = QHBoxLayout()
        self.in_air_widget.setLayout(self.in_air_layout)
        self.in_air_title = QLabel("In Air?")
        self.in_air_title.setFixedWidth(125)
        self.in_air_label = QLabel("YES" if self.in_air else "NO")
        self.in_air_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.battery_voltage_widget.setFixedWidth(125)
        self.battery_voltage_layout = QVBoxLayout()
        self.battery_voltage_layout.setContentsMargins(0, 0, 0, 0)
        self.battery_voltage_widget.setLayout(self.battery_voltage_layout)
        self.battery_voltage_title = QLabel("Battery Voltage")
        self.battery_voltage_layout.addWidget(self.battery_voltage_title)
        self.battery_voltage_label = QLabel(f"{self.battery_voltage:.2f} V")
        self.battery_voltage_layout.addWidget(self.battery_voltage_label)
        self.battery_layout.addWidget(self.battery_voltage_widget)
        # ------
        self.battery_percentage_container = QWidget()
        self.battery_percentage_layout = QHBoxLayout()
        self.battery_percentage_layout.setContentsMargins(0, 0, 0, 0)
        self.battery_percentage_container.setLayout(self.battery_percentage_layout)
        self.battery_percentage_widget = QProgressBar()
        self.battery_percentage_widget.setValue(0)
        self.battery_percentage_widget.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid grey;
                        text-align: center;
                    }

                    QProgressBar::chunk {
                        background-color: #3add36;
                        width: 1px;
                        border-radius: 5px;
                    }
                """)
        self.battery_percentage_layout.addWidget(self.battery_percentage_widget)
        self.battery_layout.addWidget(self.battery_percentage_container)
        self.layout.addWidget(self.battery_widget)

        self.setLayout(self.layout)


class UIVehicleDirection(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox { 
                border: 2px solid rgba(200,200,200, 1); 
                font-size: 14px; 
                border-radius: 15px; 
                margin: 2px;
                margin-top: 10px;
                position: relative;
            }
            QGroupBox::title {
                font-size: 18px;    
                background-color: white;
                position: absolute;
                top: -10px;
                left: 15px;
                padding-left:4px;
                padding-right:4px;
            }
        """)
        self.setTitle("Vehicle Direction")
        font_temp = self.font()
        font_temp.setBold(True)
        self.setFont(font_temp)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        # ---
        self.flight_mode = FlightMode.MANUAL
        self.flight_mode_widget = QWidget()
        self.flight_mode_layout = QVBoxLayout()
        self.flight_mode_widget.setLayout(self.flight_mode_layout)
        self.flight_mode_title = QLabel("Flight Mode")
        self.flight_mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.flight_mode_layout.addWidget(self.flight_mode_title)
        self.flight_mode_label = QLabel(f'{"Manual" if FlightMode.MANUAL else "Mission"} Mode')
        self.flight_mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.flight_mode_layout.addWidget(self.flight_mode_label)
        layout.addWidget(self.flight_mode_widget)

        # ---
        self.position: Position = Position(0, 0, 0)
        self.position_widget = QGroupBox("Position")
        self.position_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(150,150,150, 1); 
                border-radius: 10px;
            }
        """)
        self.position_layout = QHBoxLayout()
        self.position_widget.setLayout(self.position_layout)
        self.position_titles_labels = {
            "lat": {"title": QLabel("Lat"), "label": QLabel(f"{self.position.latitude} m")},
            "lon": {"title": QLabel("Lon"), "label": QLabel(f"{self.position.longitude} m")},
            "alt": {"title": QLabel("Alt"), "label": QLabel(f"{self.position.altitude} m")}
        }

        for pos in self.position_titles_labels.keys():
            wid = QWidget()
            lay = QVBoxLayout()
            wid.setLayout(lay)
            lay.addWidget(self.position_titles_labels[pos]["title"])
            self.position_titles_labels[pos]["title"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(self.position_titles_labels[pos]["label"])
            self.position_titles_labels[pos]["label"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.position_layout.addWidget(wid)

        layout.addWidget(self.position_widget)

        # ---
        self.attitude: Attitude = Attitude(0, 0, 0)
        self.attitude_widget = QGroupBox("Attitude")
        self.attitude_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(150,150,150, 1); 
                border-radius: 10px;
            }
        """)
        self.attitude_layout = QHBoxLayout()
        self.attitude_widget.setLayout(self.attitude_layout)
        self.attitude_titles_labels = {
            "lat": {"title": QLabel("Roll"), "label": QLabel(f"{self.attitude.roll} m")},
            "lon": {"title": QLabel("Pitch"), "label": QLabel(f"{self.attitude.pitch} m")},
            "alt": {"title": QLabel("Yaw"), "label": QLabel(f"{self.attitude.yaw} m")}
        }

        for pos in self.attitude_titles_labels.keys():
            wid = QWidget()
            lay = QVBoxLayout()
            wid.setLayout(lay)
            lay.addWidget(self.attitude_titles_labels[pos]["title"])
            self.attitude_titles_labels[pos]["title"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(self.attitude_titles_labels[pos]["label"])
            self.attitude_titles_labels[pos]["label"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.attitude_layout.addWidget(wid)

        layout.addWidget(self.attitude_widget)

        self.setLayout(layout)




if __name__ == "__main__":
    vehicle_status = VehicleStatus()

    the_connection = mavutil.mavlink_connection('udpin:localhost:14540')

    app = QApplication(sys.argv)

    font_database = QFontDatabase()

    for i, font in enumerate(os.listdir("../resources/fonts")):
        font_database.addApplicationFont(f"../resources/fonts/{font}")

    view = MainWindow()
    view.show()

    sys.exit(app.exec())
