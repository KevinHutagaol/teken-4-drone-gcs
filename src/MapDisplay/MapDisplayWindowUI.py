from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5 import QtWebEngineWidgets
import folium, folium.plugins
import os

from dotenv import load_dotenv

load_dotenv()


class MapDisplayWindow:
    pass


class MapDisplayWindowUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("--- Map Display ---")
        layout.addWidget(self.label)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setMinimumSize(QSize(640, 480))

        self.folium_map = generate_folium_map()

        map_widget = QtWebEngineWidgets.QWebEngineView()
        map_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        map_widget.setHtml(self.folium_map.get_root().render())
        print(self.folium_map.get_root().render())
        layout.addWidget(map_widget)


def generate_folium_map() -> folium.Map:
    tile_url = f"https://tiles.stadiamaps.com/tiles/alidade_satellite/{'{z}'}/{'{x}'}/{'{y}'}{'{r}'}.jpg?api_key={os.environ.get('STADIA_API_KEY')}"
    attribution = '© CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | © <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> © <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

    folium_map = folium.Map(location=[-6.200000, 106.816666], tiles=tile_url, attr=attribution, zoom_start=16)

    folium.plugins.MousePosition().add_to(folium_map)

    rt_source = folium.JsCode("""
    (responseHandler, errorHandler) => {
        var url = 'https://api.wheretheiss.at/v1/satellites/25544';

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
    rt.add_to(folium_map)

    return folium_map
