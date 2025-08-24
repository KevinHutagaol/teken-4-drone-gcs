from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QWidget, QVBoxLayout, QLabel

from VehicleStatus import FlightMode, Position, Attitude


class VehicleDirectionUI(QGroupBox):
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
