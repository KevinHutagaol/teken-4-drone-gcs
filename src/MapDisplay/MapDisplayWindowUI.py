import json

from PyQt5 import QtCore

from PyQt5.QtCore import QSize, QUrl, QObject, pyqtSlot, QVariant, pyqtSignal, QModelIndex
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QVBoxLayout, QGroupBox, QTextEdit, QListWidget, \
    QListWidgetItem, QPushButton, QScrollArea, QTreeWidget, QTreeWidgetItem, QHeaderView, QLineEdit

from VehicleControl import VehicleControl, WaypointListItem
from VehicleStatus import Position


class MapDisplayWindow:
    is_add_waypoint_button_checked = False

    def __init__(self, view: 'MapDisplayWindowUI', model: 'VehicleControl'):
        self._view = view
        self._model = model
        self._setup_map_logic()


    def _setup_map_logic(self):
        self._view.map_finished_loading_signal.connect(self._init_map)

    def _init_map(self):
        self._view.map_clicked_signal.connect(self._on_map_clicked)

        self._view.add_waypoint_button_clicked_signal.connect(self._on_add_waypoint_button_clicked)

        # self._view.list_current_item_changed_signal.connect(self.list_current_item_changed_slot)

        self.update_map_on_drone_move()

    def _on_add_waypoint_button_clicked(self, checked):
        self.is_add_waypoint_button_checked = checked
        self._view.map_on_add_waypoint_button_clicked(checked)

    def update_map_on_drone_move(self):
        self._view.render_waypoints_ui(self._model.get_current_pos(), self._model.get_waypoints(), -1)

    @pyqtSlot(QObject)
    def list_current_item_changed_slot(self, e):
        print(e)

    def _on_map_clicked(self, args):
        if not self.is_add_waypoint_button_checked:
            return

        alt_val = self._view.get_alt_text_input_value()

        if alt_val is None:
            self.is_add_waypoint_button_checked = False
            self._view.map_on_add_waypoint_button_clicked(False)

            return

        self._model.add_waypoint_to_end(Position(args['lat'], args['lng'], alt_val))

        self._view.render_waypoints_ui(self._model.get_current_pos(), self._model.get_waypoints(), -1)

        print(self._view.get_current_selected_list_item().data())


        self.is_add_waypoint_button_checked = False
        self._view.map_on_add_waypoint_button_clicked(False)


class MapDisplayWindowUI(QWidget):
    map_clicked_signal = pyqtSignal(QVariant)

    map_finished_loading_signal = pyqtSignal()

    window_closed_signal = pyqtSignal()

    add_waypoint_button_clicked_signal = pyqtSignal(bool)

    list_current_item_changed_signal = pyqtSignal(QObject)

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.map_widget = WebView()
        self.map_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_widget.setMinimumSize(100, 100)
        self.map_widget.load(QUrl("qrc:///map.html"))

        layout.addWidget(self.map_widget)

        self.sidebar = QWidget()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.sidebar.setFixedWidth(335)

        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)

        self.waypoint_widget = QGroupBox("Way Point")
        self.waypoint_widget.setStyleSheet("""
            QGroupBox {
                margin-top: 5px;
                border: 1px solid rgba(150,150,150, 1); 
                border-radius: 10px;
            }
                
            QGroupBox::title {
                position: absolute;
                top: -5px;
                left: 15px;
                padding-left:4px;
                padding-right:4px;
            }
        """)

        # ------------------------

        self.waypoint_widget_layout = QVBoxLayout()
        self.waypoint_widget_layout.setContentsMargins(0, 25, 0, 25)
        self.waypoint_widget_layout.setSpacing(0)
        self.waypoint_widget.setLayout(self.waypoint_widget_layout)

        self.list = QTreeWidget()
        self.list.setRootIsDecorated(False)
        self.list.setContentsMargins(0, 0, 0, 0)
        self.list.setMaximumHeight(250)
        self.list.setAlternatingRowColors(True)
        self.list.header().setSectionsMovable(False)
        self.list.header().setDragEnabled(False)
        self.list.header().setSectionResizeMode(QHeaderView.Fixed)
        self.list.setStyleSheet("""
            QTreeView::item:hover:!selected {
                color: black;
                background-color: transparent;
            }
            
            QTreeView {
                border: none; 
                border-top: 1px solid gray;
                border-bottom: 1px solid gray;
            }
        """)

        self.list.setColumnCount(5)
        self.list.setHeaderLabels(['No.', 'lat', 'lng', 'alt', ''])
        self.list.setColumnWidth(0, 5)
        self.list.setColumnWidth(1, 74)
        self.list.setColumnWidth(2, 74)
        self.list.setColumnWidth(3, 67)
        self.list.setColumnWidth(4, 10)

        self.q_tree_widget_items: list['QTreeWidgetItem'] = []

        # self.list.currentItemChanged.connect(lambda x: print(x.text()))

        self.waypoint_widget_layout.addWidget(self.list)

        self.alt_text_input_container = QWidget()

        # ---

        self.alt_text_input_layout = QHBoxLayout()
        self.alt_text_input_container.setLayout(self.alt_text_input_layout)

        self.alt_text_input_layout.addWidget(QLabel("Altitude :"))

        self.alt_text_input_layout.addSpacing(10)

        self.alt_text_input_line_edit = QLineEdit()

        self.double_validator = QDoubleValidator(0, 9999, 2)
        self.double_validator.setNotation(QDoubleValidator.StandardNotation)

        self.alt_text_input_line_edit.setValidator(self.double_validator)
        self.alt_text_input_layout.addWidget(self.alt_text_input_line_edit)

        self.alt_text_input_layout.addSpacing(1)

        self.alt_text_input_layout.addWidget(QLabel("m"))

        # ---

        self.waypoint_widget_layout.addWidget(self.alt_text_input_container)

        self.no_alt_warning_label = QLabel("")

        self.no_alt_warning_label.setStyleSheet("""
            QLabel {
                color: red; 
                font-weight: bold;
            }
        """)

        self.no_alt_warning_label.setContentsMargins(5, -5, 0, 5)

        self.waypoint_widget_layout.addWidget(self.no_alt_warning_label)

        self.add_waypoint_button = QPushButton("Add Waypoint")

        self.add_waypoint_button.setCheckable(True)

        self.waypoint_widget_layout.addWidget(self.add_waypoint_button)

        self.waypoint_widget_layout.addStretch()

        # -----------------------

        self.sidebar_layout.addWidget(self.waypoint_widget)

        layout.addWidget(self.sidebar)

        self.setMinimumSize(QSize(640, 480))

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.map_widget.handler.map_clicked.connect(self.map_clicked_signal)
        self.add_waypoint_button.clicked.connect(self.add_waypoint_button_clicked_signal)
        self.map_widget.loadFinished.connect(self.map_finished_loading_signal)
        # self.list.currentItemChanged.connect(self.list_current_item_changed_signal)

    def map_on_add_waypoint_button_clicked(self, checked):
        self.map_widget.page().runJavaScript(f"map_on_add_waypoint_button_clicked({"true" if checked else "false"})")
        self.add_waypoint_button.setChecked(checked)

    def get_alt_text_input_value(self) -> float | None:
        val = self.alt_text_input_line_edit.text()

        if val == '':
            self.no_alt_warning_label.setText("Please enter an Altitude")
            return None

        self.no_alt_warning_label.setText("")

        return float(self.alt_text_input_line_edit.text())

    def get_current_selected_list_item(self):
        return self.list.currentIndex()

    def render_waypoints_ui(self, drone_position: 'Position', waypoints: list['WaypointListItem'],
                            selectedItemNumber: int):
        self.list.clear()
        self.q_tree_widget_items = []

        waypoint_js_repr = []
        drone_position_js_repr = [drone_position.latitude, drone_position.longitude]

        for waypoint in waypoints:
            item = QTreeWidgetItem()
            item.setText(0, f"{waypoint['num']}")
            item.setText(1, f"{waypoint['waypoint'].latitude:.6f}°")
            item.setText(2, f"{waypoint['waypoint'].longitude:.6f}°")
            item.setText(3, f"{waypoint['waypoint'].altitude:.2f}m")

            self.q_tree_widget_items.append(item)

            self.list.addTopLevelItem(item)

            self.list.setItemWidget(item, 4, QPushButton("X"))

            waypoint_js_repr.append([waypoint['waypoint'].latitude, waypoint['waypoint'].longitude])

        self.map_widget.page().runJavaScript(
            f'renderMarkers({json.dumps(drone_position_js_repr)},{json.dumps(waypoint_js_repr)}, {selectedItemNumber})'
        )

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.window_closed_signal.emit()




class CallHandler(QObject):
    map_clicked = pyqtSignal(QVariant)

    def __init__(self):
        super().__init__()

    @pyqtSlot(QVariant, result=QVariant)
    def send_click_coordinates(self, args):
        self.map_clicked.emit(args)


class WebView(QWebEngineView):

    def __init__(self):
        super().__init__()

        self.channel = QWebChannel()
        self.handler = CallHandler()

        self.channel.registerObject('handler', self.handler)
        self.page().setWebChannel(self.channel)
