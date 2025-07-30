from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5 import QtWebEngineWidgets
import folium, folium.plugins

class MapDisplayWindow:
    pass

class MapDisplayWindowUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("--- Map Display ---")
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setMinimumSize(QSize(640, 480))

        self.folium_map = generate_folium_map()

        map_widget = QtWebEngineWidgets.QWebEngineView()
        map_widget.setHtml(self.folium_map.get_root().render())
        # print(self.folium_map.get_root().render())
        layout.addWidget(map_widget)


def generate_folium_map() -> folium.Map:
    folium_map = folium.Map(location=[-6.200000, 106.816666], zoom_start=13)
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
