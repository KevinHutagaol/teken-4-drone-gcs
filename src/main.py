import asyncio
import sys
import signal
import threading

from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

import time
from DroneModel import DroneModel

from MainWindow.MainWindow import MainWindow, MainWindowUI

# Stupid rendering bug in windows (apparently)
# exit code -1073740771 (0xC000041D)
# TODO: please look for more info on this
QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)

# noinspection PyUnresolvedReferences
import resources_rc

TAKEOFF_ALTITUDE = 5.0


def sigint_handler(*args):
    print("\nShutting Down")
    QApplication.quit()
    exit(0)


async def connect_to_drone(drone: "DroneModel", altitude: float):
    while not drone.get_vehicle_status().heartbeat:
        print("Waiting for heartbeat...")
        await asyncio.sleep(2.0)

    drone.arm_sync()

    while not drone.get_vehicle_status().armed:
        await asyncio.sleep(1.0)

    drone.takeoff_sync(altitude)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    load_dotenv()

    app = QApplication(sys.argv)
    drone = DroneModel("udpin://0.0.0.0:14540")

    main_view = MainWindowUI()
    MainWindow(view=main_view, model=drone)

    drone.start()
    main_view.show()

    timeout = 15

    connect_thread = threading.Thread(
        target=asyncio.run,
        args=(connect_to_drone(drone, TAKEOFF_ALTITUDE),)
    )

    connect_thread.start()

    sys.exit(app.exec_())
