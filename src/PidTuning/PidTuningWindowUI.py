from PyQt5 import QtWidgets
from PidTuning.rate_tab import RateTab
from PidTuning.attitude_tab import AttitudeTab
from PidTuning.velocity_tab import VelocityTab
from PidTuning.position_tab import PositionTab

class PidTuningWindowUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Self")
        self.resize(1036, 521) 

        self.setWindowTitle("PID Tuning Modular")
        layout = QtWidgets.QVBoxLayout(self)

        self.tabWidget = QtWidgets.QTabWidget()
        layout.addWidget(self.tabWidget)
        self.tabWidget.addTab(RateTab(), "Rate Controller")
        self.tabWidget.addTab(AttitudeTab(), "Attitude Controller")
        self.tabWidget.addTab(VelocityTab(), "Velocity Controller")
        self.tabWidget.addTab(PositionTab(), "Position Controller")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())