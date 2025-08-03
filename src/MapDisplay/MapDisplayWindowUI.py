import os

import folium
import folium.plugins
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout


class MapDisplayWindow:
    def __init__(self, view: 'MapDisplayWindowUI', model):
        self._view = view
        self._setup_map_logic()

    def _setup_map_logic(self):
        self._view.map_widget.loadFinished.connect(
            lambda _: \
                self._view.map_widget.page().runJavaScript("""
                    let qtWebChannelScript = document.createElement('script');
                    qtWebChannelScript.setAttribute('src','qrc:///qtwebchannel/qwebchannel.js');
                    document.head.appendChild(qtWebChannelScript);
                    console.log("REEEEEEEEE")
                """)
        )


class MapDisplayWindowUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.folium_map = FoliumMap()

        self.map_widget = QtWebEngineWidgets.QWebEngineView()
        self.map_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_widget.setHtml(self.folium_map.get_html())

        # print(self.folium_map.get_html())
        layout.addWidget(self.map_widget)

        self.label = QLabel("--- Map Display ---")
        layout.addWidget(self.label)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setMinimumSize(QSize(640, 480))


class FoliumMap:
    def __init__(self):
        tile_url = f"https://tiles.stadiamaps.com/tiles/alidade_satellite/{'{z}'}/{'{x}'}/{'{y}'}{'{r}'}.jpg?api_key={os.environ.get('STADIA_API_KEY')}"
        attribution = (
            '© CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | © <a '
            'href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> © <a '
            'href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> © <a '
            'href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors')

        self.folium_map = folium.Map(location=[-6.200000, 106.816666], tiles=tile_url, attr=attribution, zoom_start=16,
                                     max_zoom=20)

        rt_source = folium.JsCode("""
        (responseHandler, errorHandler) => {
            let url = 'https://api.wheretheiss.at/v1/satellites/25544';

            fetch(url)
            .then((response) => {
                return response.json().then((data) => {
                    var { id, longitude, latitude } = data;

                    return {
                        'type': 'FeatureCollection',
                        'features': [{
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [longitude, latitude]
                            },
                            'properties': {
                                'id': id
                            }
                        }]
                    };
                })
            })
            .then(responseHandler)
            .catch(errorHandler);
        }
        """)

        rt = folium.plugins.Realtime(rt_source, interval=5000)
        rt.add_to(self.folium_map)

        formatter = """
        (num) => {
            return L.Util.formatNum(num, 3) + ' &deg; ';
        };
        """

        mouse_pos = folium.plugins.MousePosition(
            position="topright",
            separator=" | ",
            empty_string="",
            lng_first=True,
            num_digits=20,
            prefix="Coordinates:",
            lat_formatter=formatter,
            lng_formatter=formatter,
        )

        mouse_pos.add_to(self.folium_map)

        self.html = None

    def get_html(self):
        return self.folium_map.get_root().render()
