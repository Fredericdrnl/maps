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

# HTML pour popup/menu
html_menu = """
<div id="popup" style="
    position: fixed;
    top: 10px;
    right: 10px;
    width: 300px;
    max-height: 500px;
    overflow-y: auto;
    background:white;
    z-index:9999;
    padding:10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
">
    <button id="searchBtn">Recherche client</button>
    <button id="createBtn">Créer client</button>
</div>
"""

m.get_root().html.add_child(folium.Element(html_menu))

# JS Script pour filtre dynamique, ajout et suppression
js_script = """
<script>
var markers = [];
var allClients = [];

function getMap() { 
    for (var key in window) { 
        if (key.startsWith("map_")) return window[key]; 
    } 
    return null; 
}

// Charger clients depuis API
async function loadAllClients() {
    const map = getMap();
    if(!map) return;
    try {
        const res = await fetch('http://127.0.0.1:5000/clients');
        allClients = await res.json();
        createMarkers(allClients);
        updateMarkers();
    } catch(err) { console.error("Erreur chargement clients:", err); }
}

function createMarkers(clients) {
    const map = getMap();
    markers = [];
    clients.forEach(c => {
        if(c.latitude && c.longitude) {
            let m = L.marker([c.latitude, c.longitude], {
                icon:L.AwesomeMarkers.icon({icon:'info-sign', markerColor:c.couleur||'blue'})
            }).bindPopup(`<b>${c.nom_client}</b><br>
                          Code: ${c.code_client}<br>
                          Jours: ${c.jours_livraison}<br>
                          Tournée: ${c.tournee}<br>
                          Adresse: ${c.adresse_complete}<br>
                          <button onclick="deleteClient(${c.id}, markers.find(mk => mk.clientId===${c.id}))">Supprimer</button>`);
            m.clientId = c.id;
            markers.push(m);
        }
    });
}

function updateMarkers({jours=null, nom=null}={}) {
    const map = getMap();
    if(!map) return;
    let visibleMarkers = [];
    markers.forEach(m => {
        let c = allClients.find(c => c.id === m.clientId);
        let show = true;
        if(jours && jours.length>0) show = jours.some(j => c.jours_livraison.includes(j));
        if(show && nom) show = c.nom_client.toLowerCase().includes(nom.toLowerCase());
        if(show) { if(!map.hasLayer(m)) m.addTo(map); visibleMarkers.push([c.latitude, c.longitude]); }
        else { if(map.hasLayer(m)) map.removeLayer(m); }
    });
    if(visibleMarkers.length>0) map.fitBounds(L.latLngBounds(visibleMarkers).pad(0.2));
}

async function deleteClient(id, marker) {
    if(!confirm("Supprimer ce client ?")) return;
    try {
        const res = await fetch(`http://127.0.0.1:5000/clients/${id}`, { method:'DELETE' });
        if(res.ok) {
            const map = getMap();
            if(marker && map.hasLayer(marker)) map.removeLayer(marker);
            markers = markers.filter(m => m.clientId !== id);
            allClients = allClients.filter(c => c.id !== id);
        }
    } catch(err) { console.error("Erreur suppression client:", err); alert("Erreur lors de la suppression !"); }
}

document.addEventListener("DOMContentLoaded", function(){
    loadAllClients();
    const popup = document.getElementById("popup");

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
            updateMarkers({jours:selectedDays, nom:nameFilter});
        }

        checkboxes.forEach(cb => cb.addEventListener('change', update));
        nameInput.addEventListener('input', update);
    };

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
            const res = await fetch("http://127.0.0.1:5000/clients", {
                method:"POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify(client)
            });
            const newClient = await res.json();
            client.id = newClient.id;
            allClients.push(client);

            let map = getMap();
            let m = L.marker([client.latitude, client.longitude], {
                icon:L.AwesomeMarkers.icon({icon:'info-sign', markerColor:client.couleur||'blue'})
            }).bindPopup(`<b>${client.nom_client}</b><br>
                          Code: ${client.code_client}<br>
                          Jours: ${client.jours_livraison}<br>
                          Tournée: ${client.tournee}<br>
                          Adresse: ${client.adresse_complete}<br>
                          <button onclick="deleteClient(${client.id}, markers.find(mk => mk.clientId===${client.id}))">Supprimer</button>`);
            m.clientId = client.id;
            markers.push(m);
            updateMarkers();
            popup.style.display="none";
        };
    };
});
</script>
"""

m.get_root().html.add_child(folium.Element(js_script))

# --- SAUVEGARDE ---
m.save("carte_menu_centre_popup_haut_gauche.html")
print("✅ Carte générée : carte_menu_centre_popup_haut_gauche.html")

