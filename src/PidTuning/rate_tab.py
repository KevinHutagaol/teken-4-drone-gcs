from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets

class RateTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rate Control")
        self.default_Kp = 1.0
        self.default_Ki = 0.1
        self.default_Kd = 0.01
        self.Kp_Rate = self.default_Kp
        self.Ki_Rate = self.default_Ki
        self.Kd_Rate = self.default_Kd
        self.tuning_mode = "Roll"
        self.init_ui()
        self.init_graphRate_plot()
        self.update_graphRate_plot()  # Tampilkan chart awal

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        # --- Grafik di kiri ---
        graph_widget = QtWidgets.QWidget()
        graph_layout = QtWidgets.QVBoxLayout(graph_widget)
        self.graphRate = QtWidgets.QWidget()
        graph_layout.addWidget(self.graphRate)
        main_layout.addWidget(graph_widget, stretch=2)

        # --- PID Gain & Control Button di kanan ---
        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout(control_widget)

        pid_group = QtWidgets.QGroupBox("PID Gain & Select Tuning")
        pid_layout = QtWidgets.QHBoxLayout(pid_group)

        self.tuning_select = QtWidgets.QComboBox()
        self.tuning_select.addItems(["Roll", "Pitch", "Yaw"])
        self.tuning_select.setCurrentIndex(0)
        self.tuning_select.currentTextChanged.connect(self.on_tuning_changed)
        pid_layout.addWidget(self.tuning_select)

        self.kp_box = QtWidgets.QDoubleSpinBox()
        self.kp_box.setPrefix("P: ")
        self.kp_box.setValue(self.Kp_Rate)
        self.kp_box.setDecimals(3)
        self.kp_box.setSingleStep(0.01)
        pid_layout.addWidget(self.kp_box)

        self.ki_box = QtWidgets.QDoubleSpinBox()
        self.ki_box.setPrefix("I: ")
        self.ki_box.setValue(self.Ki_Rate)
        self.ki_box.setDecimals(3)
        self.ki_box.setSingleStep(0.01)
        pid_layout.addWidget(self.ki_box)

        self.kd_box = QtWidgets.QDoubleSpinBox()
        self.kd_box.setPrefix("D: ")
        self.kd_box.setValue(self.Kd_Rate)
        self.kd_box.setDecimals(3)
        self.kd_box.setSingleStep(0.01)
        pid_layout.addWidget(self.kd_box)

        control_layout.addWidget(pid_group)

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
        self.btn_auto.clicked.connect(self.reset_pid_gain)

        main_layout.addWidget(control_widget, stretch=1)

    def on_tuning_changed(self, text):
        self.tuning_mode = text

    def init_graphRate_plot(self):
        self.graphRate_fig = Figure(figsize=(4, 2), dpi=100)
        self.graphRate_ax = self.graphRate_fig.add_subplot(111)
        self.graphRate_canvas = FigureCanvas(self.graphRate_fig)
        layout = QtWidgets.QVBoxLayout(self.graphRate)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graphRate_canvas)

    def update_graphRate_plot(self):
        # Ambil nilai Kp, Ki, Kd dari variabel (bukan spinbox langsung)
        w = self.graphRate.width() / self.graphRate_canvas.figure.dpi
        h = self.graphRate.height() / self.graphRate_canvas.figure.dpi
        self.graphRate_fig.set_size_inches(max(w, 2), max(h, 1), forward=True)
        
        kp = self.Kp_Rate
        ki = self.Ki_Rate
        kd = self.Kd_Rate

        x_labels = ['P', 'I', 'D']
        y_values = [kp, ki, kd]
        bar_colors = ['red', 'green', 'blue']

        self.graphRate_ax.clear()
        bars = self.graphRate_ax.bar(x_labels, y_values, color=bar_colors, width=0.6)
        self.graphRate_ax.set_xlabel('Komponen')
        self.graphRate_ax.set_ylabel('Nilai')
        self.graphRate_ax.set_title(f"PID - {self.tuning_mode} Rate")
        self.graphRate_ax.grid(True, linestyle='--', alpha=0.5)

        # Tambahkan value di atas bar
        for bar in bars:
            height = bar.get_height()
            self.graphRate_ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.3f}",
                ha='center',
                va='bottom',
                fontsize=10,
                color='black'
            )

        self.graphRate_fig.tight_layout()
        self.graphRate_canvas.draw()

    def pause_graphRate(self):
        pass  # Tidak perlu timer, chart hanya update saat submit

    def continue_graphRate(self):
        pass  # Tidak perlu timer, chart hanya update saat submit

    def submit_pid_gain(self):
        self.Kp_Rate = self.kp_box.value()
        self.Ki_Rate = self.ki_box.value()
        self.Kd_Rate = self.kd_box.value()
        self.update_graphRate_plot()

    def reset_pid_gain(self):
        self.Kp_Rate = self.default_Kp
        self.Ki_Rate = self.default_Ki
        self.Kd_Rate = self.default_Kd
        self.kp_box.setValue(self.default_Kp)
        self.ki_box.setValue(self.default_Ki)
        self.kd_box.setValue(self.default_Kd)
        self.update_graphRate_plot()