from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets
import csv, os, numpy as np

class AttitudeTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attitude Control")
        # PID values for each axis
        self.pid_values = {
            "Roll": {"P": 6.5, "I": 0.0, "D": 0.0},
            "Pitch": {"P": 6.5, "I": 0.0, "D": 0.0}, 
            "Yaw": {"P": 2.8, "I": 0.0, "D": 0.0}
        }
        self.tuning_mode = "Roll"
        self.init_ui()
        self.update_pid_chart()
        
    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        
        # Left side - Bar Chart
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.figure.patch.set_facecolor('white')
        
        left_layout.addWidget(self.canvas)
        main_layout.addWidget(left_widget, stretch=2)
        
        # Right side - Controls
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        
        # Select Tuning Radio Buttons
        tuning_group = QtWidgets.QGroupBox("Select Tuning :")
        tuning_layout = QtWidgets.QHBoxLayout(tuning_group)
        
        self.radio_roll = QtWidgets.QRadioButton("Roll")
        self.radio_pitch = QtWidgets.QRadioButton("Pitch")
        self.radio_yaw = QtWidgets.QRadioButton("Yaw")
        self.radio_roll.setChecked(True)
        
        self.radio_roll.toggled.connect(lambda: self.on_tuning_changed("Roll") if self.radio_roll.isChecked() else None)
        self.radio_pitch.toggled.connect(lambda: self.on_tuning_changed("Pitch") if self.radio_pitch.isChecked() else None)
        self.radio_yaw.toggled.connect(lambda: self.on_tuning_changed("Yaw") if self.radio_yaw.isChecked() else None)
        
        tuning_layout.addWidget(self.radio_roll)
        tuning_layout.addWidget(self.radio_pitch)
        tuning_layout.addWidget(self.radio_yaw)
        right_layout.addWidget(tuning_group)
        
        # PID Parameter inputs
        pid_widget = QtWidgets.QWidget()
        pid_layout = QtWidgets.QFormLayout(pid_widget)
        
        self.p_spinbox = QtWidgets.QDoubleSpinBox()
        self.p_spinbox.setRange(0, 100)
        self.p_spinbox.setDecimals(2)
        self.p_spinbox.setSingleStep(0.01)
        self.p_spinbox.setValue(self.pid_values[self.tuning_mode]["P"])
        self.p_spinbox.valueChanged.connect(self.on_pid_changed)
        
        self.i_spinbox = QtWidgets.QDoubleSpinBox()
        self.i_spinbox.setRange(0, 100)
        self.i_spinbox.setDecimals(2)
        self.i_spinbox.setSingleStep(0.01)
        self.i_spinbox.setValue(self.pid_values[self.tuning_mode]["I"])
        self.i_spinbox.valueChanged.connect(self.on_pid_changed)
        
        self.d_spinbox = QtWidgets.QDoubleSpinBox()
        self.d_spinbox.setRange(0, 100)
        self.d_spinbox.setDecimals(2)
        self.d_spinbox.setSingleStep(0.01)
        self.d_spinbox.setValue(self.pid_values[self.tuning_mode]["D"])
        self.d_spinbox.valueChanged.connect(self.on_pid_changed)
        
        pid_layout.addRow("P", self.p_spinbox)
        pid_layout.addRow("I", self.i_spinbox)
        pid_layout.addRow("D", self.d_spinbox)
        right_layout.addWidget(pid_widget)
        
        # Control Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_pause = QtWidgets.QPushButton("Pause")
        self.btn_continue = QtWidgets.QPushButton("Continue")
        self.btn_auto = QtWidgets.QPushButton("Auto")
        self.btn_submit = QtWidgets.QPushButton("Submit")
        
        button_layout.addWidget(self.btn_pause)
        button_layout.addWidget(self.btn_continue)
        button_layout.addWidget(self.btn_auto)
        button_layout.addWidget(self.btn_submit)
        
        self.btn_pause.clicked.connect(self.pause_control)
        self.btn_continue.clicked.connect(self.continue_control)
        self.btn_submit.clicked.connect(self.submit_pid_values)
        
        right_layout.addLayout(button_layout)
        main_layout.addWidget(right_widget, stretch=1)
        
    def on_tuning_changed(self, mode):
        self.tuning_mode = mode
        self.update_pid_inputs()
        self.update_pid_chart()
        
    def on_pid_changed(self):
        self.pid_values[self.tuning_mode]["P"] = self.p_spinbox.value()
        self.pid_values[self.tuning_mode]["I"] = self.i_spinbox.value()
        self.pid_values[self.tuning_mode]["D"] = self.d_spinbox.value()
        self.update_pid_chart()
        
    def update_pid_inputs(self):
        self.p_spinbox.setValue(self.pid_values[self.tuning_mode]["P"])
        self.i_spinbox.setValue(self.pid_values[self.tuning_mode]["I"])
        self.d_spinbox.setValue(self.pid_values[self.tuning_mode]["D"])
        
    def update_pid_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get current PID values
        p_val = self.pid_values[self.tuning_mode]["P"]
        i_val = self.pid_values[self.tuning_mode]["I"]
        d_val = self.pid_values[self.tuning_mode]["D"]
        
        # Create bar chart
        categories = ['P', 'I', 'D']
        values = [p_val, i_val, d_val]
        colors = ['red', 'blue', 'green']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{value:.3f}', ha='center', va='bottom')
        
        ax.set_title(f'Attitude PID Parameters - {self.tuning_mode}')
        ax.set_ylabel('Value')
        ax.set_ylim(0, max(max(values) * 1.2, 5))
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def pause_control(self):
        print(f"Attitude control paused for {self.tuning_mode}")
        
    def continue_control(self):
        print(f"Attitude control continued for {self.tuning_mode}")
        
    def submit_pid_values(self):
        print(f"Attitude PID values submitted for {self.tuning_mode}:")
        print(f"P: {self.pid_values[self.tuning_mode]['P']}")
        print(f"I: {self.pid_values[self.tuning_mode]['I']}")
        print(f"D: {self.pid_values[self.tuning_mode]['D']}")
