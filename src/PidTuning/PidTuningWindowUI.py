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
        
        self.rate_tab = RateTab()
        self.attitude_tab = AttitudeTab()
        self.velocity_tab = VelocityTab()
        self.position_tab = PositionTab()
        
        self.tabWidget.addTab(self.rate_tab, "Rate Controller")
        self.tabWidget.addTab(self.attitude_tab, "Attitude Controller")
        self.tabWidget.addTab(self.velocity_tab, "Velocity Controller")
        self.tabWidget.addTab(self.position_tab, "Position Controller")
        
        self.setup_connections()
        
    def is_drone_connected(self):
        return self.drone_model is not None
    
    def get_connection_status(self):
        if not self.drone_model:
            return "DroneModel: None"
        
        if hasattr(self.drone_model, 'status'):
            try:
                status = self.drone_model.status()
                return f"DroneModel: Connected, Heartbeat: {status.heartbeat}"
            except:
                return "DroneModel: Available but status unavailable"
        
        return "DroneModel: Available"
    
    def setup_connections(self):
        if not self.is_drone_connected():
            return
            
        if hasattr(self.rate_tab, 'pid_submitted'):
            self.rate_tab.pid_submitted.connect(self._handle_rate_pid_submit)
        if hasattr(self.rate_tab, 'load_from_drone'):
            self.rate_tab.load_from_drone.connect(self._load_rate_pid_from_drone)
            
        if hasattr(self.attitude_tab, 'pid_submitted'): 
            self.attitude_tab.pid_submitted.connect(self._handle_attitude_pid_submit)
        if hasattr(self.attitude_tab, 'load_from_drone'):
            self.attitude_tab.load_from_drone.connect(self._load_attitude_pid_from_drone)
            
        if hasattr(self.velocity_tab, 'pid_submitted'):
            self.velocity_tab.pid_submitted.connect(self._handle_velocity_pid_submit)
        if hasattr(self.velocity_tab, 'load_from_drone'):
            self.velocity_tab.load_from_drone.connect(self._load_velocity_pid_from_drone)
            
        if hasattr(self.position_tab, 'pid_submitted'):
            self.position_tab.pid_submitted.connect(self._handle_position_pid_submit)
        if hasattr(self.position_tab, 'load_from_drone'):
            self.position_tab.load_from_drone.connect(self._load_position_pid_from_drone)
    
    def _handle_rate_pid_submit(self, axis, p, i, d):
        self.drone_model.set_rate_pid_params_sync(p, i, d, axis.lower())
    
    def _handle_attitude_pid_submit(self, axis, p, i, d):
        self.drone_model.set_attitude_pid_params_sync(p, i, d, axis.lower())
    
    def _handle_velocity_pid_submit(self, axis, p, i, d):
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        self.drone_model.set_velocity_pid_params_sync(p, i, d, px4_axis)
    
    def _handle_position_pid_submit(self, axis, p, i, d):
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        self.drone_model.set_position_pid_params_sync(p, i, d, px4_axis)
    
    def _load_rate_pid_from_drone(self, axis):
        params = self.drone_model.get_rate_pid_params_sync(axis.lower())
        if params:
            self.rate_tab.update_pid_values_from_drone(axis, params)
    
    def _load_attitude_pid_from_drone(self, axis):
        params = self.drone_model.get_attitude_pid_params_sync(axis.lower())
        if params:
            self.attitude_tab.update_pid_values_from_drone(axis, params)
    
    def _load_velocity_pid_from_drone(self, axis):
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        params = self.drone_model.get_velocity_pid_params_sync(px4_axis)
        if params:
            self.velocity_tab.update_pid_values_from_drone(axis, params)
    
    def _load_position_pid_from_drone(self, axis):
        px4_axis = "x" if axis.lower() == "horizontal" else "z"
        params = self.drone_model.get_position_pid_params_sync(px4_axis)
        if params:
            self.position_tab.update_pid_values_from_drone(axis, params)
