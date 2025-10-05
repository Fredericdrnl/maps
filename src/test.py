import folium

# Bornes du Nord de la France
lat_min, lat_max = 49, 51.5
lon_min, lon_max = 1, 4.5
lat_step, lon_step = 0.2, 0.3

m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles="OpenStreetMap")

def add_grid_cells(map_object, lat_step, lon_step, bounds):
    lat_min, lat_max, lon_min, lon_max = bounds
    lat = lat_min
    i = 0
    while lat < lat_max:
        lon = lon_min
        j = 0
        while lon < lon_max:
            coords = [
                (lat, lon),
                (lat + lat_step, lon),
                (lat + lat_step, lon + lon_step),
                (lat, lon + lon_step),
                (lat, lon)
            ]
            folium.Polygon(
                coords, color="blue", weight=1,
                fill=True, fill_opacity=0.1,
                popup=f"Cellule (i={i}, j={j})"
            ).add_to(map_object)
            lon += lon_step
            j += 1
        lat += lat_step
        i += 1

add_grid_cells(m, lat_step, lon_step, [lat_min, lat_max, lon_min, lon_max])

# Sidebar + progress bar (centrée en haut)
html_sidebar = """
<div id="sidebar" style="
    position: fixed;
    top: 10px;
    right: 10px;
    width: 360px;
    height: 540px;
    background-color: white;
    z-index:9999;
    padding: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.25);
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
    <ul id="cityList" style="padding-left:10px; margin-top:5px; max-height:200px; overflow:auto;"></ul>
    <hr>
    <h4>Importer un fichier CSV</h4>
    <input type="file" id="csvFile" accept=".csv" style="width: 100%; margin-bottom:8px;">
    <button id="clearCacheBtn" style="width:100%; margin-bottom:8px;">Vider le cache (localStorage)</button>
</div>

<!-- ✅ Barre de progression centrée en haut -->
<div id="progressContainer" style="
    display:none;
    position: fixed;
    top: 15px;
    left: 50%;
    transform: translateX(-50%);
    width: 40%;
    background-color: rgba(255,255,255,0.95);
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    padding: 12px;
    text-align: center;
    z-index: 10000;
    font-family: Arial, sans-serif;
">
    <div style="font-size:14px; margin-bottom:6px;">Import en cours...</div>
    <div style="width:100%; background:#eee; height:14px; border-radius:7px;">
        <div id="progressBar" style="width:0%; height:14px; background:#4CAF50; border-radius:7px;"></div>
    </div>
    <div id="progressText" style="font-size:12px; margin-top:5px;">0%</div>
    <div id="progressCount" style="font-size:13px; margin-top:3px; color:#333;">0 / 0 adresses</div>
</div>
"""
m.get_root().html.add_child(folium.Element(html_sidebar))

# JS principal avec compteur dynamique
js_script = """
<script>
var markerDict = {};
var geoCache = JSON.parse(localStorage.getItem('geoCache') || '{}');

function saveCache() {
    try {
        localStorage.setItem('geoCache', JSON.stringify(geoCache));
    } catch (e) {
        console.warn("Impossible de sauvegarder le cache dans localStorage :", e);
    }
}

function addCityMarker(map) {
    var input = document.getElementById('city');
    var colorSelect = document.getElementById('cityColor');

    input.addEventListener("keypress", function(event) {
        if(event.key === "Enter") {
            event.preventDefault();
            var city = input.value.trim();
            if(city === "") return;
            var color = colorSelect.value;
            processAddress(map, city, color, function(){});
            input.value = "";
        }
    });
}

function addMarker(map, city, lat, lon, color) {
    var marker = L.marker([lat, lon], {
        icon: L.AwesomeMarkers.icon({
            icon: 'info-sign',
            markerColor: color.toLowerCase()
        })
    }).addTo(map).bindPopup(city + " (" + color + ")");
    var key = city + "@" + lat + "," + lon;
    markerDict[key] = marker;

    var li = document.createElement("li");
    li.textContent = city + " ";
    li.style.cursor = 'pointer';

    var btn = document.createElement("button");
    btn.textContent = "Supprimer";
    btn.style.marginLeft = "5px";
    btn.onclick = function() {
        map.removeLayer(marker);
        li.remove();
        delete markerDict[key];
    };

    li.onclick = function(e) {
        if(e.target.tagName !== 'BUTTON') {
            map.setView([lat, lon], 12);
            marker.openPopup();
        }
    };

    li.appendChild(btn);
    document.getElementById("cityList").appendChild(li);
}

function processAddress(map, address, color, doneCallback) {
    var key = address.toLowerCase().trim();
    var allowedColors = [
        'red','blue','green','orange','purple','darkred','darkblue','darkgreen',
        'cadetblue','darkpurple','white','pink','lightblue','lightgreen','gray',
        'black','lightgray'
    ];
    if (!allowedColors.includes(color.toLowerCase())) color = 'blue';

    if (geoCache[key]) {
        var c = geoCache[key];
        addMarker(map, address, c.lat, c.lon, color);
        if (doneCallback) doneCallback(null, true);
        return;
    }

    fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(address))
    .then(response => response.json())
    .then(data => {
        if (data && data.length > 0) {
            var lat = parseFloat(data[0].lat);
            var lon = parseFloat(data[0].lon);
            geoCache[key] = {lat: lat, lon: lon};
            saveCache();
            addMarker(map, address, lat, lon, color);
            if (doneCallback) doneCallback(null, false);
        } else {
            console.log("Adresse non trouvée :", address);
            if (doneCallback) doneCallback("notfound", false);
        }
    }).catch(function(err){
        console.error("Erreur fetch Nominatim:", err);
        if (doneCallback) doneCallback(err, false);
    });
}

function importCSV(map) {
    var fileInput = document.getElementById('csvFile');
    var clearBtn = document.getElementById('clearCacheBtn');

    clearBtn.addEventListener('click', function(){
        if (confirm("Vider le cache local des géocodages ?")) {
            geoCache = {};
            localStorage.removeItem('geoCache');
            alert("Cache vidé.");
        }
    });

    fileInput.addEventListener('change', function(e) {
        var file = e.target.files[0];
        if(!file) return;
        var reader = new FileReader();
        reader.onload = function(event) {
            var text = event.target.result;
            var lines = text.split(/\\r?\\n/).filter(line => line.trim() !== '');
            if (lines.length === 0) return;

            var progressContainer = document.getElementById('progressContainer');
            var progressBar = document.getElementById('progressBar');
            var progressText = document.getElementById('progressText');
            var progressCount = document.getElementById('progressCount');
            progressContainer.style.display = 'block';

            var total = lines.length;
            var processed = 0;

            function updateProgress() {
                var pct = Math.round((processed / total) * 100);
                progressBar.style.width = pct + '%';
                progressText.textContent = pct + '%';
                progressCount.textContent = processed + " / " + total + " adresses";
            }

            function finishImport() {
                processed = total;
                updateProgress();
                progressText.textContent = "✅ Import terminé";
                setTimeout(function(){
                    progressContainer.style.display = 'none';
                }, 2000);
            }

            function processLine(index) {
                if (index >= lines.length) return finishImport();

                var line = lines[index].trim();
                var lastComma = line.lastIndexOf(',');
                if (lastComma === -1) {
                    processed++;
                    updateProgress();
                    setTimeout(()=>processLine(index+1), 0);
                    return;
                }

                var color = line.substring(lastComma + 1).trim().replace(/"/g,'');
                var address = line.substring(0, lastComma).trim().replace(/"/g,'');

                if (!address) {
                    processed++;
                    updateProgress();
                    setTimeout(()=>processLine(index+1), 0);
                    return;
                }

                var cacheKey = address.toLowerCase();
                var delay = 0;
                if (geoCache[cacheKey]) delay = 0; else delay = 1000;

                processAddress(map, address, color, function(){
                    processed++;
                    updateProgress();
                    setTimeout(()=>processLine(index+1), delay);
                });
            }

            processLine(0);
        };
        reader.readAsText(file);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    for (var key in window) {
        if (key.startsWith("map_")) {
            var map = window[key];
            addCityMarker(map);
            importCSV(map);
        }
    }
});
</script>
"""
m.get_root().html.add_child(folium.Element(js_script))

m.save("index.html")
