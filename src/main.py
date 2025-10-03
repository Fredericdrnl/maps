import folium
from folium import IFrame

# Définition des bornes du Nord de la France
lat_min, lat_max = 49, 51.5
lon_min, lon_max = 1, 4.5
lat_step, lon_step = 0.2, 0.3  # Cases plus petites (~11 km en latitude)

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
            # Coordonnées de la case (carré en degrés)
            coords = [
                (lat, lon),
                (lat + lat_step, lon),
                (lat + lat_step, lon + lon_step),
                (lat, lon + lon_step),
                (lat, lon)
            ]
            
            # Polygone interactif avec indices
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

# Ajouter les cases
add_grid_cells(m, lat_step, lon_step, [lat_min, lat_max, lon_min, lon_max])

# Ajouter le panneau latéral fixe
html_sidebar = """
<div id="sidebar" style="
    position: fixed;
    top: 10px;
    right: 10px;
    width: 250px;
    height: 200px;
    background-color: white;
    z-index:9999;
    padding: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
    overflow-y: auto;
">
    <h4>Ajouter une ville</h4>
    <input type="text" id="city" placeholder="Nom de la ville" style="width: 100%;">
    <ul id="cityList" style="padding-left:10px; margin-top:5px;"></ul>
</div>
"""
m.get_root().html.add_child(folium.Element(html_sidebar))

# Ajouter le script JS
js_script = """
<script>
function addCityMarker(map) {
    var input = document.getElementById('city');
    input.addEventListener("keypress", function(event) {
        if(event.key === "Enter") {
            event.preventDefault();
            var city = input.value.trim();
            if(city === "") { return; }

            // Appel API Nominatim
            fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + city)
              .then(response => response.json())
              .then(data => {
                  if(data.length > 0) {
                      var lat = parseFloat(data[0].lat);
                      var lon = parseFloat(data[0].lon);

                      // Ajouter le marqueur
                      L.marker([lat, lon], {
                        icon: L.AwesomeMarkers.icon({
                            icon: 'info-sign',
                            markerColor: 'green'
                        })
                      }).addTo(map)
                       .bindPopup(city)
                       .openPopup();

                      // Centrer la carte sur la ville
                      map.setView([lat, lon], 12);

                      // Ajouter la ville à la liste
                      var li = document.createElement("li");
                      li.textContent = city;
                      document.getElementById("cityList").appendChild(li);

                      input.value = "";
                  } else {
                      alert("Ville non trouvée !");
                  }
              });
        }
    });
}

// Attendre que la carte Folium soit chargée
document.addEventListener("DOMContentLoaded", function() {
    for (var key in window) {
        if (key.startsWith("map_")) {
            addCityMarker(window[key]);
        }
    }
});
</script>
"""

m.get_root().html.add_child(folium.Element(js_script))

# Sauvegarde
m.save("index.html")
