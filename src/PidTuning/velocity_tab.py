from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets
import csv, os, numpy as np

class VelocityTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velocity Control")
        self.Kp_Velo = 1.0
        self.Ki_Velo = 0.1
        self.Kd_Velo = 0.01
        self.tuning_mode = "Horizontal"
        self.init_ui()
        self.init_graphVelo_plot()
        self.graphVelo_timer = QtCore.QTimer()
        self.graphVelo_timer.timeout.connect(self.update_graphVelo_plot)
        self.graphVelo_timer.start(1000)

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)  # Horizontal layout utama

        # --- Grafik di kiri ---
        graph_widget = QtWidgets.QWidget()
        graph_layout = QtWidgets.QVBoxLayout(graph_widget)
        self.graphVelo = QtWidgets.QWidget()
        graph_layout.addWidget(self.graphVelo)
        self.scrollbarVelo = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        graph_layout.addWidget(self.scrollbarVelo)
        self.scrollbarVelo.valueChanged.connect(self.update_graphVelo_plot)
        main_layout.addWidget(graph_widget, stretch=2)

        # --- PID Gain & Control Button di kanan ---
        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout(control_widget)

        # PID Gain Box with Select Tuning
        pid_group = QtWidgets.QGroupBox("PID Gain & Select Tuning")
        pid_layout = QtWidgets.QHBoxLayout(pid_group)

        # Select Tuning ComboBox
        self.tuning_select = QtWidgets.QComboBox()
        self.tuning_select.addItems(["Horizontal", "Vertical"])
        self.tuning_select.setCurrentIndex(0)  # Default: Horizontal
        self.tuning_select.currentTextChanged.connect(self.on_tuning_changed)
        pid_layout.addWidget(self.tuning_select)

        self.kp_box = QtWidgets.QDoubleSpinBox()
        self.kp_box.setPrefix("Kp: ")
        self.kp_box.setValue(self.Kp_Velo)
        self.kp_box.setDecimals(3)
        self.kp_box.setSingleStep(0.01)
        pid_layout.addWidget(self.kp_box)

        self.ki_box = QtWidgets.QDoubleSpinBox()
        self.ki_box.setPrefix("Ki: ")
        self.ki_box.setValue(self.Ki_Velo)
        self.ki_box.setDecimals(3)
        self.ki_box.setSingleStep(0.01)
        pid_layout.addWidget(self.ki_box)

        self.kd_box = QtWidgets.QDoubleSpinBox()
        self.kd_box.setPrefix("Kd: ")
        self.kd_box.setValue(self.Kd_Velo)
        self.kd_box.setDecimals(3)
        self.kd_box.setSingleStep(0.01)
        pid_layout.addWidget(self.kd_box)

        control_layout.addWidget(pid_group)

        # Button Box
        btn_group = QtWidgets.QGroupBox("Control Buttons")
        btn_layout = QtWidgets.QHBoxLayout(btn_group)
        self.btn_pause = QtWidgets.QPushButton("Pause")
        self.btn_continue = QtWidgets.QPushButton("Continue")
        self.btn_auto = QtWidgets.QPushButton("Auto")
        self.btn_submit = QtWidgets.QPushButton("Submit")
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_continue)
        btn_layout.addWidget(self.btn_auto)
        btn_layout.addWidget(self.btn_submit)
        control_layout.addWidget(btn_group)

        # Connect buttons
        self.btn_pause.clicked.connect(self.pause_graphVelo)
        self.btn_continue.clicked.connect(self.continue_graphVelo)
        self.btn_submit.clicked.connect(self.submit_pid_gain)

        main_layout.addWidget(control_widget, stretch=1)

    def on_tuning_changed(self, text):
        self.tuning_mode = text
        # You can add logic here to change Kp, Ki, Kd values based on selection if needed

    def init_graphVelo_plot(self):
        self.graphVelo_fig = Figure(figsize=(4, 2), dpi=100)
        self.graphVelo_ax = self.graphVelo_fig.add_subplot(111)
        self.graphVelo_canvas = FigureCanvas(self.graphVelo_fig)
        layout = QtWidgets.QVBoxLayout(self.graphVelo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graphVelo_canvas)

    def update_graphVelo_plot(self):
        detik, value, value_ubah = [], [], []
        window_size = 10
        if os.path.exists("log.csv"):
            with open("log.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        detik.append(int(row["detik"]))
                        value.append(float(row["value"]))
                        value_ubah.append(float(row["value"]) * (self.Kp_Velo + self.Ki_Velo + self.Kd_Velo))
                    except Exception:
                        continue
        if len(detik) > window_size:
            self.scrollbarVelo.setMaximum(len(detik) - window_size)
        else:
            self.scrollbarVelo.setMaximum(0)
            self.scrollbarVelo.setValue(0)
        start_idx = self.scrollbarVelo.value()
        end_idx = start_idx + window_size
        detik_window = detik[start_idx:end_idx]
        value_window = value[start_idx:end_idx]
        value_ubah_window = value_ubah[start_idx:end_idx]
        self.graphVelo_ax.clear()
        self.graphVelo_ax.set_title(f"graphVelo Live - {self.tuning_mode}")
        self.graphVelo_ax.set_xlabel("Detik")
        self.graphVelo_ax.set_ylabel("Value")
        self.graphVelo_ax.grid(True)
        if detik_window and value_window:
            self.graphVelo_ax.plot(detik_window, value_window, color='g')
            self.graphVelo_ax.plot(detik_window, value_ubah_window, color='r')
            self.graphVelo_ax.legend(["Value", "Value Ubah"])
        self.graphVelo_canvas.draw()

    def pause_graphVelo(self):
        self.graphVelo_timer.stop()

    def continue_graphVelo(self):
        self.graphVelo_timer.start(1000)

    def submit_pid_gain(self):
        self.Kp_Velo = self.kp_box.value()
        self.Ki_Velo = self.ki_box.value()
        self.Kd_Velo = self.kd_box.value()
        self.update_graphVelo_plot()