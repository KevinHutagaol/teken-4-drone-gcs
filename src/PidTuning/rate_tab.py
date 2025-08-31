from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv, os, numpy as np

class RateTab(QtWidgets.QWidget):
    pid_submitted = pyqtSignal(str, float, float, float)
    load_from_drone = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rate Control")
        self.pid_values = {
            "Roll": {"P": 4.0, "I": 0.0, "D": 0.0},
            "Pitch": {"P": 4.0, "I": 0.0, "D": 0.0}, 
            "Yaw": {"P": 4.0, "I": 0.0, "D": 0.0}
        }
        self.tuning_mode = "Roll"
        self.init_ui()
        self.update_pid_chart()

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.figure.patch.set_facecolor('white')
        
        left_layout.addWidget(self.canvas)
        main_layout.addWidget(left_widget, stretch=2)
        
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        
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
        button_layout1 = QtWidgets.QHBoxLayout()
        self.btn_load = QtWidgets.QPushButton("Load from Drone")
        self.btn_submit = QtWidgets.QPushButton("Submit to Drone")
        
        button_layout1.addWidget(self.btn_load)
        button_layout1.addWidget(self.btn_submit)
        right_layout.addLayout(button_layout1)
        
        self.btn_submit.clicked.connect(self.submit_pid_values)
        self.btn_load.clicked.connect(self.load_pid_from_drone)
        
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
        
        ax.set_title(f'Rate PID Parameters - {self.tuning_mode}')
        ax.set_ylabel('Value')
        ax.set_ylim(0, max(max(values) * 1.2, 5))
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def submit_pid_values(self):
        p = self.pid_values[self.tuning_mode]['P']
        i = self.pid_values[self.tuning_mode]['I']
        d = self.pid_values[self.tuning_mode]['D']
        
        self.pid_submitted.emit(self.tuning_mode, p, i, d)
        
    def load_pid_from_drone(self):
        self.load_from_drone.emit(self.tuning_mode)
        
    def update_pid_values_from_drone(self, axis, params):
        if axis in self.pid_values and params:
            self.pid_values[axis]["P"] = params.get("p", 0.0)
            self.pid_values[axis]["I"] = params.get("i", 0.0)
            self.pid_values[axis]["D"] = params.get("d", 0.0)
            
            if axis == self.tuning_mode:
                self.update_pid_inputs()
                self.update_pid_chart()