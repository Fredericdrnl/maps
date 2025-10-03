import folium

# Définition des bornes du Nord de la France
lat_min, lat_max = 49, 51.5
lon_min, lon_max = 1, 4.5
lat_step, lon_step = 0.2, 0.3

# Création de la carte
m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles="OpenStreetMap")

# Fonction pour créer un quadrillage
def add_grid_cells(map_object, lat_step, lon_step, bounds):
    lat_min, lat_max, lon_min, lon_max = bounds
    i = 0
    lat = lat_min
    while lat < lat_max:
        j = 0
        lon = lon_min
        while lon < lon_max:
            coords = [
                (lat, lon),
                (lat + lat_step, lon),
                (lat + lat_step, lon + lon_step),
                (lat, lon + lon_step),
                (lat, lon)
            ]
            folium.Polygon(
                coords,
                color="blue",
                weight=1,
                fill=True,
                fill_opacity=0.1,
                popup=f"Cellule (i={i}, j={j})"
            ).add_to(map_object)
            lon += lon_step
            j += 1
        lat += lat_step
        i += 1

add_grid_cells(m, lat_step, lon_step, [lat_min, lat_max, lon_min, lon_max])

# Panneau latéral
html_sidebar = """
<div id="sidebar" style="
    position: fixed;
    top: 10px;
    right: 10px;
    width: 320px;
    height: 450px;
    background-color: white;
    z-index:9999;
    padding: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
    overflow-y: auto;
">
    <h4>Ajouter une ville</h4>
    <input type="text" id="city" placeholder="Nom de la ville" style="width: 100%; margin-bottom:5px;">
    <select id="cityColor" style="width:100%; margin-bottom:5px;">
        <option value="red">Red</option>
        <option value="blue" selected>Blue</option>
        <option value="green">Green</option>
        <option value="orange">Orange</option>
        <option value="purple">Purple</option>
        <option value="darkred">DarkRed</option>
        <option value="darkblue">DarkBlue</option>
        <option value="darkgreen">DarkGreen</option>
        <option value="cadetblue">CadetBlue</option>
        <option value="darkpurple">DarkPurple</option>
        <option value="white">White</option>
        <option value="pink">Pink</option>
        <option value="lightblue">LightBlue</option>
        <option value="lightgreen">LightGreen</option>
        <option value="gray">Gray</option>
        <option value="black">Black</option>
        <option value="lightgray">LightGray</option>
    </select>
    <ul id="cityList" style="padding-left:10px; margin-top:5px;"></ul>
    <hr>
    <h4>Importer CSV</h4>
    <input type="file" id="csvFile" accept=".csv" style="width: 100%;">
</div>
"""
m.get_root().html.add_child(folium.Element(html_sidebar))

# Script JS avec vérification des couleurs
js_script = """
<script>
var markerDict = {};

function addCityMarker(map) {
    var input = document.getElementById('city');
    var colorSelect = document.getElementById('cityColor');

    input.addEventListener("keypress", function(event) {
        if(event.key === "Enter") {
            event.preventDefault();
            var city = input.value.trim();
            if(city === "") return;
            var color = colorSelect.value;
            addMarker(map, city, color);
            input.value = "";
        }
    });
}

function addMarker(map, city, color) {
    // Couleurs autorisées L.AwesomeMarkers
    var allowedColors = [
        'red','blue','green','orange','purple','darkred','darkblue','darkgreen',
        'cadetblue','darkpurple','white','pink','lightblue','lightgreen','gray',
        'black','lightgray'
    ];



    fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(city))
    .then(response => response.json())
    .then(data => {
        if(data.length > 0) {
            var lat = parseFloat(data[0].lat);
            var lon = parseFloat(data[0].lon);

            var marker = L.marker([lat, lon], {
                icon: L.AwesomeMarkers.icon({
                    icon: 'info-sign',
                    markerColor: color
                })
            }).addTo(map).bindPopup(city);

            markerDict[city] = marker;

            var li = document.createElement("li");
            li.textContent = city + " ";
            li.style.cursor = 'pointer';

            var btn = document.createElement("button");
            btn.textContent = "Supprimer";
            btn.style.marginLeft = "5px";
            btn.onclick = function() {
                map.removeLayer(marker);
                li.remove();
                delete markerDict[city];
            };

            li.onclick = function(e) {
                if(e.target.tagName !== 'BUTTON') {
                    map.setView([lat, lon], 12);
                    marker.openPopup();
                }
            };

            li.appendChild(btn);
            document.getElementById("cityList").appendChild(li);

            map.setView([lat, lon], 12);
        } else {
            alert("Adresse non trouvée: " + city);
        }
    });
}

function importCSV(map) {
    var fileInput = document.getElementById('csvFile');
    fileInput.addEventListener('change', function(e) {
        var file = e.target.files[0];
        if(!file) return;
        var reader = new FileReader();
        reader.onload = function(event) {
            var text = event.target.result;
            var lines = text.split('\\n');
            for(var i=0; i<lines.length; i++) {
                var line = lines[i].trim();
                if(line === '') continue;
                var parts = line.split(',');
                var address = parts[0] + " " + parts[1] + " " + parts[2];
                var color = parts[3];
                addMarker(map, address, color);
            }
        };
        reader.readAsText(file);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    for(var key in window) {
        if(key.startsWith("map_")) {
            var map = window[key];
            addCityMarker(map);
            importCSV(map);
        }
    }
});
</script>
"""
m.get_root().html.add_child(folium.Element(js_script))

# Sauvegarde
m.save("index.html")
