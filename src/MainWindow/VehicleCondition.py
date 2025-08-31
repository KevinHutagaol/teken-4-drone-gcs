from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QProgressBar


class VehicleConditionUI(QGroupBox):
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
        self.heartbeat_widget = QWidget()
        self.heartbeat_layout = QHBoxLayout()
        self.heartbeat_widget.setLayout(self.heartbeat_layout)
        self.heartbeat_title = QLabel("Heartbeat")
        self.heartbeat_title.setFixedWidth(125)
        self.heartbeat_label = QLabel("Offline")
        self.heartbeat_label.setStyleSheet("font-weight: bold; color: #800000")
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



    def set_condition_values(self, heartbeat: bool, in_air, battery_voltage: float, battery_percentage: float):
        if heartbeat:
            self.heartbeat_label.setText("Online")
            self.heartbeat_label.setStyleSheet("font-weight: bold; color: #008000")
        else:
            self.heartbeat_label.setText("Offline")
            self.heartbeat_label.setStyleSheet("font-weight: bold; color: #800000")
        self.in_air_label.setText(f"{'Yes' if in_air else 'No' }")
        self.battery_voltage_label.setText(f"{battery_voltage:.2f} V")
        self.battery_percentage_widget.setValue(int(battery_percentage))

