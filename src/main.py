import os
import sys

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

import time
import asyncio
from VehicleStatus import VehicleStatus
from DroneModel import DroneModel

from MainWindow.MainWindow import MainWindow, MainWindowUI

# Stupid rendering bug in windows (apparently)
# exit code -1073740771 (0xC000041D)
# TODO: please look for more info on this
QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)

# noinspection PyUnresolvedReferences
import resources_rc

if __name__ == "__main__":
    load_dotenv()

    app = QApplication(sys.argv)
    drone = DroneModel("udpin://0.0.0.0:14540")
    
    main_view = MainWindowUI()
    MainWindow(view=main_view)
    
    drone.start()
    main_view.show()
    
    timeout = 15 

    while not drone.vehicle_status.heartbeat:
        print("Waiting for heartbeat...")
        time.sleep(0.5)
        app.processEvents()
    
    if drone.vehicle_status.heartbeat:
        drone.arm_sync()
        drone.takeoff_sync(5)
    sys.exit(app.exec_())



    
