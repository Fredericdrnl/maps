import folium

# Créer la carte centrée sur la France
m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)

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
                      L.marker([lat, lon]).addTo(map)
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

# Sauvegarder
m.save("map_with_sidebar_working.html")
