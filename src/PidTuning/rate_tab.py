from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import csv, os, numpy as np

class RateTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rate Control")
        self.Kp_Rate = 1.0
        self.Ki_Rate = 0.1
        self.Kd_Rate = 0.01
        self.tuning_mode = "Roll"
        self.init_ui()
        self.graphRate_timer = QtCore.QTimer()
        self.graphRate_timer.timeout.connect(self.update_graphRate_plot)
        self.graphRate_timer.start(1000)

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        # --- Grafik di kiri ---
        graph_widget = QtWidgets.QWidget()
        graph_layout = QtWidgets.QVBoxLayout(graph_widget)
        self.graphRate_plot = pg.PlotWidget()
        self.graphRate_plot.setBackground('w')
        self.graphRate_plot.showGrid(x=True, y=True)
        graph_layout.addWidget(self.graphRate_plot)
        self.scrollbarrate = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        graph_layout.addWidget(self.scrollbarrate)
        self.scrollbarrate.valueChanged.connect(self.update_graphRate_plot)
        main_layout.addWidget(graph_widget, stretch=2)

        # --- PID Gain & Control Button di kanan ---
        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout(control_widget)

        # PID Gain Box with Select Tuning
        pid_group = QtWidgets.QGroupBox("PID Gain & Select Tuning")
        pid_layout = QtWidgets.QHBoxLayout(pid_group)

        self.tuning_select = QtWidgets.QComboBox()
        self.tuning_select.addItems(["Roll", "Pitch", "Yaw"])
        self.tuning_select.setCurrentIndex(0)
        self.tuning_select.currentTextChanged.connect(self.on_tuning_changed)
        pid_layout.addWidget(self.tuning_select)

        self.kp_box = QtWidgets.QDoubleSpinBox()
        self.kp_box.setPrefix("Kp: ")
        self.kp_box.setValue(self.Kp_Rate)
        self.kp_box.setDecimals(3)
        self.kp_box.setSingleStep(0.01)
        pid_layout.addWidget(self.kp_box)

        self.ki_box = QtWidgets.QDoubleSpinBox()
        self.ki_box.setPrefix("Ki: ")
        self.ki_box.setValue(self.Ki_Rate)
        self.ki_box.setDecimals(3)
        self.ki_box.setSingleStep(0.01)
        pid_layout.addWidget(self.ki_box)

        self.kd_box = QtWidgets.QDoubleSpinBox()
        self.kd_box.setPrefix("Kd: ")
        self.kd_box.setValue(self.Kd_Rate)
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

        self.btn_pause.clicked.connect(self.pause_graphRate)
        self.btn_continue.clicked.connect(self.continue_graphRate)
        self.btn_submit.clicked.connect(self.submit_pid_gain)

        main_layout.addWidget(control_widget, stretch=1)

    def on_tuning_changed(self, text):
        self.tuning_mode = text

    def update_graphRate_plot(self):
        detik, value, value_ubah = [], [], []
        window_size = 10
        if os.path.exists("log.csv"):
            with open("log.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        detik.append(int(row["detik"]))
                        value.append(float(row["value"]))
                        value_ubah.append(float(row["value"]) * (self.Kp_Rate + self.Ki_Rate + self.Kd_Rate))
                    except Exception:
                        continue
        if len(detik) > window_size:
            self.scrollbarrate.setMaximum(len(detik) - window_size)
        else:
            self.scrollbarrate.setMaximum(0)
            self.scrollbarrate.setValue(0)
        start_idx = self.scrollbarrate.value()
        end_idx = start_idx + window_size
        detik_window = np.array(detik[start_idx:end_idx])
        value_window = np.array(value[start_idx:end_idx])
        value_ubah_window = np.array(value_ubah[start_idx:end_idx])

        self.graphRate_plot.clear()
        self.graphRate_plot.setBackground('k')  # Set background to black
        self.graphRate_plot.setTitle(f"graphRate Live - {self.tuning_mode}", color='w')
        self.graphRate_plot.setLabel('bottom', "Detik", color='w')
        self.graphRate_plot.setLabel('left', "Value", color='w')

        # Add legend with custom label colors
        legend = self.graphRate_plot.addLegend()
        legend.setBrush(pg.mkBrush(0, 0, 0, 200))  # legend background black

        if detik_window.size and value_window.size:
            curve1 = self.graphRate_plot.plot(
                detik_window, value_window,
                pen=pg.mkPen('g', width=2),
                name='<span style="color:white;">Value</span>'
            )
            curve2 = self.graphRate_plot.plot(
                detik_window, value_ubah_window,
                pen=pg.mkPen('r', width=2),
                name='<span style="color:red;">Value Ubah</span>'
            )

    def pause_graphRate(self):
        self.graphRate_timer.stop()

    def continue_graphRate(self):
        self.graphRate_timer.start(1000)

    def submit_pid_gain(self):
        self.Kp_Rate = self.kp_box.value()
        self.Ki_Rate = self.ki_box.value()
        self.Kd_Rate = self.kd_box.value()
        self.update_graphRate_plot()