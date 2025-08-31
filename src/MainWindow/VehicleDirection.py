import numpy as np
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QWidget, QVBoxLayout, QLabel, QGridLayout, QSizePolicy, \
    QGraphicsDropShadowEffect

from VehicleStatus import FlightMode, Position, Attitude, Velocity


class VehicleDirectionController(QObject):
    def __init__(self):
        super().__init__()


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

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setVerticalSpacing(10)
        layout.setHorizontalSpacing(0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

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
        layout.addWidget(self.flight_mode_widget, 0, 0)

        # ---
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
            "lat": {"title": QLabel("Lat"), "label": QLabel(f"{0}°")},
            "lon": {"title": QLabel("Lon"), "label": QLabel(f"{0}°")},
            "alt": {"title": QLabel("Alt"), "label": QLabel(f"{0} m")}
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

        layout.addWidget(self.position_widget, 0, 1)

        # ---
        self.attitude_widget = QGroupBox("Attitude")
        self.attitude_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(150,150,150, 1); 
                border-radius: 10px;
            }
        """)
        # self.box_shadow = QGraphicsDropShadowEffect()
        # self.box_shadow.setBlurRadius(5)
        # self.attitude_widget.setGraphicsEffect(self.box_shadow)
        self.attitude_layout = QHBoxLayout()
        self.attitude_widget.setLayout(self.attitude_layout)
        self.attitude_titles_labels = {
            "roll": {"title": QLabel("Roll"), "label": QLabel(f"{0}°")},
            "pitch": {"title": QLabel("Pitch"), "label": QLabel(f"{0}°")},
            "yaw": {"title": QLabel("Yaw"), "label": QLabel(f"{0}°")}
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

        layout.addWidget(self.attitude_widget, 1, 0)

        # ---
        self.velocity_widget = QGroupBox("Velocity")
        self.velocity_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid rgba(150,150,150, 1); 
                border-radius: 10px;
            }
        """)
        # self.attitude_widget.setGraphicsEffect(self.box_shadow)
        self.velocity_layout = QHBoxLayout()
        self.velocity_widget.setLayout(self.velocity_layout)
        self.velocity_titles_labels = {
            "vx": {"title": QLabel("Vx"), "label": QLabel(f"{0} m/s")},
            "vy": {"title": QLabel("Vy"), "label": QLabel(f"{0} m/s")},
            "vz": {"title": QLabel("Vz"), "label": QLabel(f"{0} m/s")}
        }

        for pos in self.velocity_titles_labels.keys():
            wid = QWidget()
            lay = QVBoxLayout()
            wid.setLayout(lay)
            lay.addWidget(self.velocity_titles_labels[pos]["title"])
            self.velocity_titles_labels[pos]["title"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(self.velocity_titles_labels[pos]["label"])
            self.velocity_titles_labels[pos]["label"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.velocity_layout.addWidget(wid)

        layout.addWidget(self.velocity_widget, 1, 1)

        self.setLayout(layout)

    def set_direction_values(self, pos: "Position", att: "Attitude", vel: "Velocity", flight_mode: "FlightMode"):
        # position
        self.position_titles_labels["lat"]['label'].setText(f"{pos.latitude:.6f}°")
        self.position_titles_labels["lon"]['label'].setText(f"{pos.longitude:.6f}°")
        self.position_titles_labels["alt"]['label'].setText(f"{pos.altitude:.6f} m")
        # attitude
        self.attitude_titles_labels["roll"]['label'].setText(f"{np.rad2deg(att.roll):.2f}°")
        self.attitude_titles_labels["pitch"]['label'].setText(f"{np.rad2deg(att.pitch):.2f}°")
        self.attitude_titles_labels["yaw"]['label'].setText(f"{np.rad2deg(att.yaw):.2f}°")
        # velocity
        self.velocity_titles_labels["vx"]['label'].setText(f"{vel.vx:.2f} m/s")
        self.velocity_titles_labels["vy"]['label'].setText(f"{vel.vy:.2f} m/s")
        self.velocity_titles_labels["vz"]['label'].setText(f"{vel.vz:.2f} m/s")
        # other
        self.flight_mode_label.setText(str(flight_mode).title())
