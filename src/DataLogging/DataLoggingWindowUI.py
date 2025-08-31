import pandas as pd
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget, mkPen
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtGui import QIntValidator
import numpy as np

from DroneModel import DroneModel
from VehicleStatus import Attitude
from VehicleStatus import Position
from VehicleStatus import Velocity


class DataLoggingWindow(QObject):
    time_stamp: list[int] = []
    battery_voltage: list[float] = []
    battery_percentage: list[float] = []
    velocity: list['Velocity'] = []
    position: list['Position'] = []
    attitude: list['Attitude'] = []

    def __init__(self, view: "DataLoggingWindowUI", model: "DroneModel"):
        super().__init__()
        self._view = view
        self._model = model

        self.logging = False
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(50)
        self.interval = 50

        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self._view.set_interval_button_clicked_signal.connect(self.set_interval)
        self._view.download_log_button_clicked_signal.connect(self.download_log)
        self._view.export_csv_button_clicked_signal.connect(self.export_csv)
        self._view.log_data_button_clicked_signal.connect(self.log_data)
        self._view.combo_box_current_index_changed_signal.connect(lambda _: self.update_plot_ui())
        self.timer.timeout.connect(self.on_timer_timeout)

    @pyqtSlot()
    def update_plot_ui(self):
        index = self._view.get_combo_box_index()
        self._view.update_plot(index, self.time_stamp, self.battery_voltage, self.battery_percentage, self.velocity,
                               self.position, self.attitude)

    def on_timer_timeout(self):
        self.update_plot_data()
        self.update_plot_ui()

    @pyqtSlot()
    def update_plot_data(self):
        if len(self.time_stamp) == 0:
            self.time_stamp.append(self.interval)
        else:
            self.time_stamp.append(self.time_stamp[-1] + self.interval)

        vehicle_stat = self._model.get_vehicle_status()

        self.battery_voltage.append(vehicle_stat.battery_voltage)
        self.battery_percentage.append(vehicle_stat.battery_percentage)
        self.velocity.append(
            Velocity(vehicle_stat.velocity.vx, vehicle_stat.velocity.vy, vehicle_stat.velocity.vz)
        )
        self.position.append(
            Position(vehicle_stat.position.latitude, vehicle_stat.position.longitude, vehicle_stat.position.altitude)
        )
        self.attitude.append(
            Attitude(vehicle_stat.attitude.roll, vehicle_stat.attitude.pitch, vehicle_stat.attitude.yaw)
        )

    @pyqtSlot()
    def log_data(self):
        if not self.logging:
            self.logging = True
            self._view.set_start_stop_button_text(False)
            self.timer.start()
        else:
            self.logging = False
            self._view.set_start_stop_button_text(True)
            self.timer.stop()

    @pyqtSlot()
    def set_interval(self):
        interval = int(self._view.get_line_edit_interval())
        self.timer.setInterval(interval)
        self.interval = interval

    @pyqtSlot()
    def download_log(self):
        index = self._view.get_combo_box_index()
        if index == 0:
            plt.plot(self.time_stamp, self.battery_voltage)
            plt.ylabel("Battery Voltage $(V)$")
        elif index == 1:
            plt.plot(self.time_stamp, self.battery_percentage)
            plt.ylabel("Battery Percentage")
        elif index == 2:
            plt.plot(self.time_stamp, [vel.vx for vel in self.velocity], label="$V_x (m/s)$")
            plt.plot(self.time_stamp, [vel.vy for vel in self.velocity], label="$V_y (m/s)$")
            plt.plot(self.time_stamp, [vel.vz for vel in self.velocity], label="$V_z (m/s)$")
            plt.ylabel("Velocity")
        elif index == 3:
            plt.plot(self.time_stamp, [pos.latitude for pos in self.position], label="Latitude $(°)$")
            plt.plot(self.time_stamp, [pos.longitude for pos in self.position], label="Longitude $(°)$")
            plt.plot(self.time_stamp, [pos.altitude for pos in self.position], label="Altitude $(m)$")
            plt.ylabel("Position")
        elif index == 4:
            plt.plot(self.time_stamp, [att.roll for att in self.attitude], label="Roll $(rad)$")
            plt.plot(self.time_stamp, [att.pitch for att in self.attitude], label="Pitch $(rad)$")
            plt.plot(self.time_stamp, [att.yaw for att in self.attitude], label="Yaw $(rad)$")
            plt.ylabel("Attitude")



        plt.legend(loc="upper left")
        plt.xlabel("Time (ms)")
        plt.grid()
        plt.show()

    @pyqtSlot()
    def export_csv(self):
        drone_data_table = np.array([
            self.time_stamp,
            self.battery_percentage,
            self.battery_voltage,
            [vel.vx for vel in self.velocity],
            [vel.vy for vel in self.velocity],
            [vel.vz for vel in self.velocity],
            [pos.latitude for pos in self.position],
            [pos.longitude for pos in self.position],
            [pos.altitude for pos in self.position],
            [att.roll for att in self.attitude],
            [att.pitch for att in self.attitude],
            [att.yaw for att in self.attitude]
        ]).T
        drone_df = pd.DataFrame(
            drone_data_table,
            columns=["time(ms)", "battery_percentage(%)", "battery_voltage(V)",
                     "vx(m/s)", "vy(m/s)", "vz(m/s)",
                     "lat(°)", "lon(°)", "alt(m)",
                     "roll(rad)", "pitch(rad)", "yaw(rad)"]
        )

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            "Save File",
            "drone_data.csv",
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if file_path:
            drone_df.to_csv(file_path, index=False)


class DataLoggingWindowUI(QWidget):
    window_closed_signal = pyqtSignal()

    log_data_button_clicked_signal = pyqtSignal()
    set_interval_button_clicked_signal = pyqtSignal()
    download_log_button_clicked_signal = pyqtSignal()
    export_csv_button_clicked_signal = pyqtSignal()
    combo_box_current_index_changed_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setEnabled(True)
        self.resize(640, 330)
        self.setMinimumSize(QtCore.QSize(640, 240))
        # self.setMaximumSize(QtCore.QSize(800, 16777215))

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(20, 50, 221, 31))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(['Battery Voltage', 'Battery Percentage', 'Velocity', 'Position', 'Attitude'])

        self.linEdit = QtWidgets.QLineEdit(self)
        self.linEdit.setGeometry(QtCore.QRect(20, 125, 221, 31))
        self.linEdit.setObjectName("linEdit")

        self.int_validator = QIntValidator(1, 30000)
        self.linEdit.setValidator(self.int_validator)

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(20, 95, 221, 20))
        font = QtGui.QFont()
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(20, 160, 221, 29))
        self.pushButton.setObjectName("pushButton")

        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(20, 20, 231, 20))
        font = QtGui.QFont()
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 240, 221, 29))
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 270, 221, 29))
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_4 = QtWidgets.QPushButton(self)
        self.pushButton_4.setGeometry(QtCore.QRect(20, 210, 221, 29))
        self.pushButton_4.setObjectName("pushButton_4")

        self.graphicsView_2 = PlotWidget(self)
        self.graphicsView_2.setGeometry(QtCore.QRect(260, 20, 361, 291))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.graphicsView_2.setTitle("Battery Voltage")
        self.graphicsView_2.setBackground("w")
        self.graphicsView_2.addLegend()

        self.data_line_a = self.graphicsView_2.plot([], [], pen=mkPen(color=(0, 114, 178), width=2), name="Component A")
        self.data_line_b = self.graphicsView_2.plot([], [], pen=mkPen(color=(230, 159, 0), width=2), name="Component B")
        self.data_line_c = self.graphicsView_2.plot([], [], pen=mkPen(color=(213, 94, 0), width=2), name="Component C")
        self.graphicsView_2.getPlotItem().legend.setVisible(False)

        self.retranslateUi()

        self.connect_signals_and_slots()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Widget", "Data Logger"))
        self.setWindowIcon(QtGui.QIcon(':/clock_00.png'))
        self.label_2.setText(_translate("Widget", "Logging Interval (Milliseconds)"))
        self.pushButton.setText(_translate("Widget", "Set Interval"))
        self.label_3.setText(_translate("Widget", "Data Type"))
        self.pushButton_2.setText(_translate("Widget", "Start Logging"))
        self.pushButton_3.setText(_translate("Widget", "Download Log"))
        self.pushButton_4.setText(_translate("Widget", "Export CSV File"))

    @pyqtSlot(int)
    def update_plot(self, index, time_stamp: list[int], battery_voltage: float, battery_percentage: float,
                    velocity: list['Velocity'], position: list['Position'], attitude: list['Attitude']):
        legend = self.graphicsView_2.getPlotItem().legend
        if index == 0:
            self.data_line_a.setData(time_stamp, battery_voltage)
            self.data_line_b.clear()
            self.data_line_c.clear()
            self.graphicsView_2.setTitle("Battery Voltage")
            legend.setVisible(False)
        elif index == 1:
            self.data_line_a.setData(time_stamp, battery_percentage)
            self.data_line_b.clear()
            self.data_line_c.clear()
            self.graphicsView_2.setTitle("Battery Percentage")
            legend.setVisible(False)
        elif index == 2:
            self.data_line_a.setData(time_stamp, [vel.vx for vel in velocity])
            self.data_line_b.setData(time_stamp, [vel.vy for vel in velocity])
            self.data_line_c.setData(time_stamp, [vel.vz for vel in velocity])
            self.graphicsView_2.setTitle("Velocity")
            legend.setVisible(True)
            legend.getLabel(self.data_line_a).setText("Velocity X")
            legend.getLabel(self.data_line_b).setText("Velocity Y")
            legend.getLabel(self.data_line_c).setText("Velocity Z")
        elif index == 3:
            self.data_line_a.setData(time_stamp, [pos.latitude for pos in position])
            self.data_line_b.setData(time_stamp, [pos.longitude for pos in position])
            self.data_line_c.setData(time_stamp, [pos.altitude for pos in position])
            self.graphicsView_2.setTitle("Position")
            legend.setVisible(True)
            legend.getLabel(self.data_line_a).setText("Latitude")
            legend.getLabel(self.data_line_b).setText("Longitude")
            legend.getLabel(self.data_line_c).setText("Altitude")
        elif index == 4:
            self.data_line_a.setData(time_stamp, [att.roll for att in attitude])
            self.data_line_b.setData(time_stamp, [att.pitch for att in attitude])
            self.data_line_c.setData(time_stamp, [att.yaw for att in attitude])
            self.graphicsView_2.setTitle("Attitude")
            legend.setVisible(True)
            legend.getLabel(self.data_line_a).setText("Roll")
            legend.getLabel(self.data_line_b).setText("Pitch")
            legend.getLabel(self.data_line_c).setText("Yaw")

    def get_line_edit_interval(self):
        return self.linEdit.text()

    def get_combo_box_index(self):
        return self.comboBox.currentIndex()

    def set_start_stop_button_text(self, val: bool):
        if val:
            self.pushButton_2.setText("Start Logging")
            self.pushButton_2.setStyleSheet("font-weight: bold; color: #008000")
        else:
            self.pushButton_2.setText("Stop Logging")
            self.pushButton_2.setStyleSheet("font-weight: bold; color: #800000")

    def connect_signals_and_slots(self):
        self.pushButton.clicked.connect(self.set_interval_button_clicked_signal)
        self.pushButton_2.clicked.connect(self.log_data_button_clicked_signal)
        self.pushButton_3.clicked.connect(self.download_log_button_clicked_signal)
        self.pushButton_4.clicked.connect(self.export_csv_button_clicked_signal)
        self.comboBox.currentIndexChanged.connect(self.combo_box_current_index_changed_signal)

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.window_closed_signal.emit()
