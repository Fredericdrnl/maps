import folium

# --- CARTE ---
lat_min, lat_max = 49.6, 51
lon_min, lon_max = 1.5, 4
lat_step, lon_step = 0.15, 0.25

m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles="OpenStreetMap")

# --- QUADRILLAGE ---
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

html = """
<style>
#menu {
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    z-index:9999;
    padding:5px 10px;
    box-shadow:2px2px5px rgba(0,0,0,0.3);
    font-family:Arial,sans-serif;
}
#menu button { margin:0 5px; }
#popup {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 320px;
    max-height: 450px;
    overflow-y: auto;
    background: white;
    z-index:9999;
    padding:10px;
    box-shadow:2px2px5px rgba(0,0,0,0.3);
    font-family:Arial,sans-serif;
    display:none;
}
</style>

<div id="menu">
    <button id="searchBtn">Recherche client</button>
    <button id="createBtn">Créer client</button>
</div>
<div id="popup"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.awesome-markers/2.0.4/leaflet.awesome-markers.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.awesome-markers/2.0.4/leaflet.awesome-markers.css">

<script>
var markers = [];

function getMap() { 
    for (var key in window) { 
        if (key.startsWith("map_")) return window[key]; 
    } 
    return null; 
}

// Charger clients depuis l'API avec filtres dynamiques
async function loadClients({jours=null, nom=null}={}) {
    const map = getMap();
    if(!map) return;

    let url = 'http://127.0.0.1:5000/clients';
    let params = [];
    if(jours && jours.length>0) params.push('jours=' + encodeURIComponent(jours.join(',')));
    if(nom) params.push('nom=' + encodeURIComponent(nom));
    if(params.length>0) url += '?' + params.join('&');

    try {
        const res = await fetch(url);
        const clients = await res.json();

        // Supprimer anciens marqueurs
        markers.forEach(m => map.removeLayer(m));
        markers = [];

        let latlngs = [];

        clients.forEach((c,i) => {
            if(c.latitude && c.longitude) {
                let m = L.marker([c.latitude, c.longitude], {
                    icon:L.AwesomeMarkers.icon({icon:'info-sign',markerColor:c.couleur||'blue'})
                }).addTo(map);

                m.bindPopup(`<b>${c.nom_client}</b><br>
                             Code: ${c.code_client}<br>
                             Jours: ${c.jours_livraison}<br>
                             Tournée: ${c.tournee}<br>
                             Adresse: ${c.adresse_complete}<br>
                             <button onclick="deleteClient(${c.id}, markers[${i}])">Supprimer</button>`);

                markers.push(m);
                latlngs.push([c.latitude, c.longitude]);
            }
        });

        // Zoom sur tous les résultats
        if(latlngs.length>0) {
            var bounds = L.latLngBounds(latlngs);
            map.fitBounds(bounds.pad(0.3));
        }

    } catch(err) {
        console.error("Erreur chargement clients:", err);
    }
}

// Suppression instantanée d'un client
async function deleteClient(id, marker) {
    if(!confirm("Supprimer ce client ?")) return;
    try {
        const res = await fetch(`http://127.0.0.1:5000/clients/${id}`, { method:'DELETE' });
        if(res.ok) {
            const map = getMap();
            if(map && marker) {
                map.removeLayer(marker);
                markers = markers.filter(m => m !== marker);
            }
        } else {
            alert("Erreur lors de la suppression !");
        }
    } catch(err) {
        console.error("Erreur suppression client:", err);
        alert("Erreur lors de la suppression !");
    }
}

document.addEventListener("DOMContentLoaded", function(){
    const map = getMap();
    if(map) loadClients();

    const popup = document.getElementById("popup");

    // Recherche client + filtres par jours
    document.getElementById("searchBtn").onclick = () => {
        popup.style.display="block";
        const days = ['L','M','W','J','V','S','D'];
        let htmlContent = '<h4>Filtrer par jours et nom</h4>';
        htmlContent += '<input type="text" id="nameSearch" placeholder="Rechercher par nom" style="width:100%; margin-bottom:5px;"><br>';
        days.forEach(d => { htmlContent += `<label><input type="checkbox" value="${d}" checked> ${d}</label><br>`; });
        popup.innerHTML = htmlContent;

        const checkboxes = popup.querySelectorAll('input[type=checkbox]');
        const nameInput = document.getElementById("nameSearch");

        function update() {
            const selectedDays = Array.from(checkboxes).filter(c=>c.checked).map(c=>c.value);
            const nameFilter = nameInput.value.trim() || null;
            loadClients({jours:selectedDays, nom:nameFilter});
        }

        checkboxes.forEach(cb => cb.addEventListener('change', update));
        nameInput.addEventListener('input', update);
    };

    // Créer client
    document.getElementById("createBtn").onclick = () => {
        popup.style.display="block";
        popup.innerHTML = `
            <h4>Créer un client</h4>
            <input id="code_client" placeholder="Code client"><br>
            <input id="nom_client" placeholder="Nom client"><br>
            <input id="jours_livraison" placeholder="Jours (LMV)"><br>
            <input id="adresse_complete" placeholder="Adresse complète"><br>
            <input id="longitude" placeholder="Longitude"><br>
            <input id="latitude" placeholder="Latitude"><br>
            <input id="couleur" placeholder="Couleur"><br>
            <input id="tournee" type="number" placeholder="Tournée"><br>
            <button id="saveBtn">Enregistrer</button>
        `;
        document.getElementById("saveBtn").onclick = async () => {
            const client = {
                code_client: document.getElementById("code_client").value,
                nom_client: document.getElementById("nom_client").value,
                jours_livraison: document.getElementById("jours_livraison").value,
                adresse_complete: document.getElementById("adresse_complete").value,
                longitude: parseFloat(document.getElementById("longitude").value),
                latitude: parseFloat(document.getElementById("latitude").value),
                couleur: document.getElementById("couleur").value || 'blue',
                tournee: parseInt(document.getElementById("tournee").value) || 0
            };
            await fetch("http://127.0.0.1:5000/clients", {
                method:"POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify(client)
            });
            popup.style.display="none";
            loadClients();
        };
    };
});
</script>
"""

m.get_root().html.add_child(folium.Element(html))
m.save("index.html")
