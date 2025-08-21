from PyQt5.QtCore import QSize, QUrl, QObject, pyqtSlot, QVariant, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QVBoxLayout, QGroupBox, QTextEdit, QListWidget, \
    QListWidgetItem


class MapDisplayWindow:
    def __init__(self, view: 'MapDisplayWindowUI', model):
        self._view = view
        self._setup_map_logic()

    def _setup_map_logic(self):
        self._view.map_clicked_signal.connect(self._on_map_clicked)

    def _on_map_clicked(self, args):
        self._view.add_new_waypoint(args)
        print(args)


class MapDisplayWindowUI(QWidget):

    map_clicked_signal = pyqtSignal(QVariant)

    window_closed_signal = pyqtSignal()

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
        self.sidebar.setFixedWidth(200)

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

        self.waypoint_widget_layout = QVBoxLayout()
        self.waypoint_widget.setLayout(self.waypoint_widget_layout)

        self.list = QListWidget()
        self.list.setMaximumHeight(300)

        # self.list.currentItemChanged.connect(lambda x: print(x.text()))

        self.waypoint_widget_layout.addWidget(self.list)

        self.sidebar_layout.addWidget(self.waypoint_widget)

        layout.addWidget(self.sidebar)

        self.setMinimumSize(QSize(640, 480))

        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.map_widget.handler.map_clicked.connect(self.map_clicked_signal)


    @pyqtSlot(dict)
    def add_new_waypoint(self, waypoint):
        self.list.addItem(QListWidgetItem(f"{waypoint['lat']:.5f}, {waypoint['lng']:.5f}"))



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
