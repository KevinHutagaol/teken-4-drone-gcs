import sys

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication

from pymavlink import mavutil

from VehicleStatus import VehicleStatus

from MainWindow.MainWindow import MainWindow, MainWindowUI

# Stupid rendering bug in windows (apparently)
# exit code -1073740771 (0xC000041D)
# TODO: please look for more info on this
QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)

# noinspection PyUnresolvedReferences
import resources_rc

if __name__ == "__main__":
    vehicle_status = VehicleStatus()

    the_connection = mavutil.mavlink_connection('udpin:localhost:14540')

    app = QApplication(sys.argv)

    main_view = MainWindowUI()

    MainWindow(view=main_view)

    main_view.show()

    sys.exit(app.exec_())
