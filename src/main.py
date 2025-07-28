import sys

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication

from pymavlink import mavutil

from VehicleStatus import VehicleStatus

from src.MainWindow.MainWindow import MainWindowUI

import resources_rc

# Stupid rendering bug in windows (apparently)
# exit code -1073740771 (0xC000041D)
# TODO: please look for more info on this
QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)

if __name__ == "__main__":
    vehicle_status = VehicleStatus()

    the_connection = mavutil.mavlink_connection('udpin:localhost:14540')

    app = QApplication(sys.argv)

    view = MainWindowUI()

    view.show()

    sys.exit(app.exec_())
