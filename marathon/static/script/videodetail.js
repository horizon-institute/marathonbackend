$(function() {
    $(".tag-pointer").click(function() {
        var t = $(this).attr("data-video-time");
        $("video")[0].currentTime = t;
        return false;
    });
    var map = L.map("video-map"),
        coords = basecoords;
        
    if (locationcoords.length) {
        coords = [0,1].map(function(n) {
            return locationcoords.reduce(function(mem, coord) {
                return mem+coord[n];
            },0)/locationcoords.length;
        });
    }
    if (coords[0] !== null) {
        map.setView(coords, 12);
    }
    
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    if (geojson) {
        $.getJSON(geojson, function(data) {
            for (var i = 0, l = data.features.length; i<l; i++) {
                var feature = data.features[i];
                switch(feature.geometry.type) {
                    case "LineString":
                        L.geoJson()
                            .addTo(map)
                            .addData(feature)
                            .setStyle({
                                color: "#c00000"
                            });
                    break;
                    case "Point":
                        switch((feature.properties.name||"").toLowerCase()) {
                            case "start":
                                var colour = "#008000";
                            break;
                            case "finish":
                                var colour = "#ff0000";
                            break;
                            default:
                                var colour = "#ffffff";
                            break;
                        }
                        L.circleMarker([
                            feature.geometry.coordinates[1],
                            feature.geometry.coordinates[0]
                        ], {
                            radius: 8,
                            fillColor: colour,
                            weight: 1,
                            fillOpacity: .8
                        }).bindPopup(feature.properties.name).addTo(map);
                    break;
                }
            }
        });
    }
    
    for (var i = 0, l = locationcoords.length; i<l; i++) {
        var coord = locationcoords[i],
            latlng = coord.slice(0,2);
        L.marker(latlng).bindPopup(coord[3]).addTo(map);
        L.circle(
            latlng, coord[2], {
                weight: 1,
                color: "#000080",
                fillColor: "#000080",
                opacity: .5
            }).addTo(map);
    }
    
});