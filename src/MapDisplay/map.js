var map = L.map('map').setView([47.399, 8.546], 16)

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


var mouse_position = new L.Control.MousePosition({
    "position": "topright",
    "separator": " | ",
    "emptyString": "",
    "lngFirst": false,
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

let droneMarker = null;
let waypointMarkers = [];
let currentHighlightedMarker = -1;

function renderMarkers(dronePosition, positions, highlightedMarker) {
    if (highlightedMarker >= 0) {
        currentHighlightedMarker = highlightedMarker;
    }

    if (!droneMarker) {
        droneMarker = L.marker(dronePosition, {icon: droneIcon}).addTo(map);
    } else {
        droneMarker.setLatLng(dronePosition)
    }

    if (!waypointMarkers || waypointMarkers.length !== positions.length) {
        markersGroup.clearLayers();
        for (let i = 0; i < positions.length; i++) {
            let mark = L.marker(positions[i]).addTo(markersGroup);
            mark.setIcon(i === currentHighlightedMarker ? redIcon : grayIcon)
            waypointMarkers.push(mark)
        }
    } else {
        for (let i = 0; i < waypointMarkers.length; i++) {
            waypointMarkers[i].setLatLng(positions[i])
            waypointMarkers[i].setIcon(i === currentHighlightedMarker ? redIcon : grayIcon)
        }
    }

}

let path;

function renderPolyLine(dronePosition, positions) {
    const newPath = [dronePosition].concat(positions);

    if (path) {
        path.setLatLngs(newPath);
    } else {
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
}


new QWebChannel(qt.webChannelTransport, channel => {
    window.handler = channel.objects.handler;

    map.on('click', e => {
        console.log(e.latlng)
        window.handler.send_click_coordinates(e.latlng)
    })


})

