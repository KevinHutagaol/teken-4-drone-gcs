var map = L.map('map').setView([-6.200000, 106.816666], 16)

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var realtime = L.realtime((responseHandler, errorHandler) => {
    let url = 'https://api.wheretheiss.at/v1/satellites/25544';

    fetch(url)
        .then((response) => {
            return response.json().then((data) => {
                var {id, longitude, latitude} = data;

                return {
                    'type': 'FeatureCollection', 'features': [{
                        'type': 'Feature', 'geometry': {
                            'type': 'Point', 'coordinates': [longitude, latitude]
                        }, 'properties': {
                            'id': id
                        }
                    }]
                };
            })
        })
        .then(responseHandler)
        .catch(errorHandler);
}, {
    "start": true, "interval": 5000, "removeMissing": false,
});
map.addLayer(realtime._container);


realtime.addTo(map);


var mouse_position = new L.Control.MousePosition({
    "position": "topright",
    "separator": " | ",
    "emptyString": "",
    "lngFirst": true,
    "numDigits": 20,
    "prefix": "Coordinates:",
});
mouse_position.options["latFormatter"] =

    (num) => {
        return L.Util.formatNum(num, 3) + ' &deg; ';
    };

mouse_position.options["lngFormatter"] =

    (num) => {
        return L.Util.formatNum(num, 3) + ' &deg; ';
    };

map.addControl(mouse_position);

let droneIcon = L.icon({
    iconUrl: "qrc:///drone-icon.png",

    iconSize: [51, 51], iconAnchor: [25, 25]
})

const grayColor = '#56586c'
const redColor = '#cc0909'

const grayMarkerHtmlStyles = `
  background-color: ${grayColor};
  width: 3rem;
  height: 3rem;
  display: block;
  left: -1.5rem;
  top: -1.5rem;
  position: relative;
  border-radius: 3rem 3rem 0;
  transform: rotate(45deg);
  border: 1px solid #FFFFFF`

const redMarkerHtmlStyles = `
  background-color: ${redColor};
  width: 3rem;
  height: 3rem;
  display: block;
  left: -1.5rem;
  top: -1.5rem;
  position: relative;
  border-radius: 3rem 3rem 0;
  transform: rotate(45deg);
  border: 1px solid #FFFFFF`

const redIcon = L.divIcon({
    className: "my-custom-pin",
    iconAnchor: [0, 24],
    labelAnchor: [-6, 0],
    popupAnchor: [0, -36],
    html: `<span style="${redMarkerHtmlStyles}" />`
})

const grayIcon = L.divIcon({
    className: "my-custom-pin",
    iconAnchor: [0, 24],
    labelAnchor: [-6, 0],
    popupAnchor: [0, -36],
    html: `<span style="${grayMarkerHtmlStyles}" />`
})


// logic

let isAddWaypointButtonChecked = false

function map_on_add_waypoint_button_clicked(checked) {
    isAddWaypointButtonChecked = checked;

    if (checked) {
        document.querySelector(".leaflet-container").style.cursor = "crosshair";
    } else {
        document.querySelector(".leaflet-container").style.cursor = "";
    }
}

let markersGroup = L.layerGroup();
map.addLayer(markersGroup);

let path;

function renderMarkers(dronePosition, positions, highlightedMarker) {

    markersGroup.clearLayers();

    L.marker(dronePosition, {icon: droneIcon}).addTo(map);


    positions.forEach((pos, i) => {
        if (i === highlightedMarker) {
            L.marker([pos[0], pos[1]], {icon: redIcon}).addTo(markersGroup);
        } else {
            L.marker([pos[0], pos[1]], {icon: grayIcon}).addTo(markersGroup);
        }
    })

    if (path) {
        map.removeLayer(path);
    }

    path = L.polyline.antPath([dronePosition].concat(positions), {
        "delay": 1000,
        "dashArray": [10, 20],
        "weight": 5,
        "color": "#0000FF",
        "pulseColor": "#FFFFFF",
        "paused": false,
        "reverse": false,
        "hardwareAccelerated": true
    });

    map.addLayer(path);


}


new QWebChannel(qt.webChannelTransport, channel => {
    window.handler = channel.objects.handler;

    map.on('click', e => {
        console.log(e.latlng)
        window.handler.send_click_coordinates(e.latlng)
    })


})

