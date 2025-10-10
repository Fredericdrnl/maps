import folium

# --- CARTE ---
lat_min, lat_max = 49.6, 51
lon_min, lon_max = 1.5, 4
lat_step, lon_step = 0.15, 0.25

m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles="OpenStreetMap")

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

html = r"""
<style>
/* ===== MENU ===== */
#topMenu {
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    padding: 12px 25px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.25);
    z-index: 9999;
    display: flex;
    gap: 15px;
    font-family: Arial, sans-serif;
}

#topMenu button {
    width: 180px;
    height: 45px;
    font-size: 15px;
    font-weight: bold;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    transition: all 0.25s ease;
}

#topMenu button:hover { background: #0056b3; transform: scale(1.05); }

/* ===== POPUP CLIENT ===== */
.marker-popup {
    font-family: Arial, sans-serif;
    font-size: 15px;
    line-height: 1.4;
    padding: 10px;
    background: #ffffffee;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.25);
    width: 250px;
}

.marker-popup b { font-size: 16px; color: #007bff; }

.marker-popup .btn {
    display: inline-block;
    margin-top: 6px;
    margin-right: 5px;
    padding: 5px 10px;
    font-size: 14px;
    font-weight: bold;
    color: white;
    background-color: #007bff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.2s;
}

.marker-popup .btn:hover { background-color: #0056b3; }

/* ===== SURBRILLANCE GLOW ===== */
@keyframes glowPulse {
    0% { box-shadow: 0 0 0px rgba(255,255,0,0.8); }
    50% { box-shadow: 0 0 15px 5px rgba(255,255,0,0.7); }
    100% { box-shadow: 0 0 0px rgba(255,255,0,0.8); }
}

.glow {
    animation: glowPulse 1.5s infinite;
    border-radius: 50%;
}

</style>

<div id="topMenu">
<button id="searchBtn">🔍 Recherche client</button>
<button id="createBtn">➕ Créer client</button>
</div>

<script>
var map = null;
var markers = [];
var allClients = [];

function getMap(){ for(var k in window) if(k.startsWith("map_")) return window[k]; return null; }

async function loadClients() {
    try {
        const res = await fetch("http://127.0.0.1:5000/clients");
        const data = await res.json();
        allClients = data;
        displayMarkers();
    } catch(e){ console.error("Erreur chargement clients:", e); }
}

function createPopupHTML(c){
    return `<div class="marker-popup">
        <b>${c.nom_client}</b><br>
        Code: ${c.code_client}<br>
        Adresse: ${c.adresse_complete || "Non renseignée"}<br>
        Jours: ${c.jours_livraison || "Non renseigné"}<br>
        Tournée: ${c.tournee || 0}<br>
        <button class='btn' onclick="deleteClient(${c.id})">Supprimer</button>
        <button class='btn' onclick="editClient(${c.id})">Modifier</button>
    </div>`;
}

function displayMarkers(){
    if(!map) map=getMap();
    markers.forEach(m => { if(map.hasLayer(m)) map.removeLayer(m); });
    markers = [];

    allClients.forEach(c => {
        if(!c.latitude || !c.longitude) return;
        const marker = L.marker([c.latitude, c.longitude])
            .bindPopup(createPopupHTML(c));
        marker.addTo(map);
        marker.client = c;
        markers.push(marker);
    });
}

function updateHighlight(filters){
    const {jours, nom, code} = filters;
    markers.forEach(m=>{
        const c = m.client;
        const matchJour = jours.length===0 || jours.some(j=>c.jours_livraison?.includes(j));
        const matchNom = !nom || c.nom_client.toLowerCase().includes(nom.toLowerCase());
        const matchCode = !code || c.code_client.toLowerCase().includes(code.toLowerCase());
        if(matchJour && matchNom && matchCode){
            if(!map.hasLayer(m)) m.addTo(map);
            if(m._icon) m._icon.classList.add("glow");
        } else {
            if(map.hasLayer(m)) map.removeLayer(m);
            if(m._icon) m._icon.classList.remove("glow");
        }
    });
}

async function deleteClient(id){
    if(!confirm("Supprimer ce client ?")) return;
    await fetch("http://127.0.0.1:5000/clients/"+id,{method:"DELETE"});
    loadClients();
}

function editClient(id){ alert("Édition non implémentée pour l'instant. ID: "+id); }

document.addEventListener("DOMContentLoaded", ()=>{
    map = getMap();
    loadClients();
});
</script>
"""

m.get_root().html.add_child(folium.Element(html))
m.save("map_clients_popup_glow.html")
print("✅ Carte prête : popups modernes, glow sur clients filtrés, boutons stylés.")