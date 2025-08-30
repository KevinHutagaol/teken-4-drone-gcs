from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject
from .rate_tab import RateTab
from .attitude_tab import AttitudeTab
from .velocity_tab import VelocityTab
from .position_tab import PositionTab

class PidTuningWindowUI(QtWidgets.QWidget):
    def __init__(self, drone_model=None):
        super().__init__()
        self.setObjectName("Self")
        self.resize(1036, 521) 
        self.drone_model = drone_model

        self.setWindowTitle("PID Tuning")
        layout = QtWidgets.QVBoxLayout(self)

        self.tabWidget = QtWidgets.QTabWidget()
        layout.addWidget(self.tabWidget)
        
        # Create tabs and store references
        self.rate_tab = RateTab()
        self.attitude_tab = AttitudeTab()
        self.velocity_tab = VelocityTab()
        self.position_tab = PositionTab()
        
        self.tabWidget.addTab(self.rate_tab, "Rate Controller")
        self.tabWidget.addTab(self.attitude_tab, "Attitude Controller")
        self.tabWidget.addTab(self.velocity_tab, "Velocity Controller")
        self.tabWidget.addTab(self.position_tab, "Position Controller")
        
        # Connect tab signals directly to drone model functions
        self.setup_connections()
    
    def setup_connections(self):
        """Connect tab signals directly to DroneModel methods"""
        if not self.drone_model:
            return
            
        # Rate tab connections
        if hasattr(self.rate_tab, 'pid_submitted'):
            self.rate_tab.pid_submitted.connect(self.on_rate_pid_submitted)
        if hasattr(self.rate_tab, 'load_from_drone'):
            self.rate_tab.load_from_drone.connect(self.on_rate_load_from_drone)
            
        # Attitude tab connections
        if hasattr(self.attitude_tab, 'pid_submitted'): 
            self.attitude_tab.pid_submitted.connect(self.on_attitude_pid_submitted)
        if hasattr(self.attitude_tab, 'load_from_drone'):
            self.attitude_tab.load_from_drone.connect(self.on_attitude_load_from_drone)
            
        # Velocity tab connections
        if hasattr(self.velocity_tab, 'pid_submitted'):
            self.velocity_tab.pid_submitted.connect(self.on_velocity_pid_submitted)
        if hasattr(self.velocity_tab, 'load_from_drone'):
            self.velocity_tab.load_from_drone.connect(self.on_velocity_load_from_drone)
            
        # Position tab connections
        if hasattr(self.position_tab, 'pid_submitted'):
            self.position_tab.pid_submitted.connect(self.on_position_pid_submitted)
        if hasattr(self.position_tab, 'load_from_drone'):
            self.position_tab.load_from_drone.connect(self.on_position_load_from_drone)
    
    def on_rate_pid_submitted(self, axis, p, i, d):
        """Submit rate PID values directly to drone model"""
        if self.drone_model:
            success = self.drone_model.set_rate_pid_params_sync(p, i, d, axis.lower())
    
    def on_rate_load_from_drone(self, axis):
        """Load rate PID values from drone model"""
        if self.drone_model:
            params = self.drone_model.get_rate_pid_params_sync(axis.lower())
            if params:
                self.rate_tab.update_pid_values_from_drone(axis, params)
        
    def on_attitude_pid_submitted(self, axis, p, i, d):
        """Submit attitude PID values directly to drone model"""
        if self.drone_model:
            success = self.drone_model.set_attitude_pid_params_sync(p, i, d, axis.lower())
    
    def on_attitude_load_from_drone(self, axis):
        """Load attitude PID values from drone model"""
        if self.drone_model:
            params = self.drone_model.get_attitude_pid_params_sync(axis.lower())
            if params:
                self.attitude_tab.update_pid_values_from_drone(axis, params)
        
    def on_velocity_pid_submitted(self, axis, p, i, d):
        """Submit velocity PID values directly to drone model"""
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        if self.drone_model:
            success = self.drone_model.set_velocity_pid_params_sync(p, i, d, px4_axis)
    
    def on_velocity_load_from_drone(self, axis):
        """Load velocity PID values from drone model"""
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        if self.drone_model:
            params = self.drone_model.get_velocity_pid_params_sync(px4_axis)
            if params:
                self.velocity_tab.update_pid_values_from_drone(axis, params)
        
    def on_position_pid_submitted(self, axis, p, i, d):
        """Submit position PID values directly to drone model"""
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        if self.drone_model:
            success = self.drone_model.set_position_pid_params_sync(p, i, d, px4_axis)
    
    def on_position_load_from_drone(self, axis):
        """Load position PID values from drone model"""
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        if self.drone_model:
            params = self.drone_model.get_position_pid_params_sync(px4_axis)
            if params:
                self.position_tab.update_pid_values_from_drone(axis, params)
