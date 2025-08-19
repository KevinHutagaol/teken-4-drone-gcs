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


// logic

let handler;

new QWebChannel(qt.webChannelTransport, channel => {

})

map.on('click', e => {
    console.log(e.latlng)
})