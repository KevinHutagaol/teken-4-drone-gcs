import sys

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication

from pymavlink import mavutil

from VehicleStatus import VehicleStatus
from VehicleCommunication import VehicleCommunication

from MainWindow.MainWindow import MainWindow, MainWindowUI

# Stupid rendering bug in windows (apparently)
# exit code -1073740771 (0xC000041D)
# TODO: please look for more info on this
QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)

# noinspection PyUnresolvedReferences
import resources_rc

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mav_connection = VehicleCommunication(port='udpin:localhost:14550')

    main_view = MainWindowUI()

    MainWindow(view=main_view)
    mav_connection.start()

    main_view.show()

    sys.exit(app.exec_())
