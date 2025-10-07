import folium

# Carte principale
m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles="OpenStreetMap")

# Menu centré et popup à droite
html_menu = """
<div id="menu" style="
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background-color: rgba(255,255,255,0.95);
    padding: 10px;
    border-radius: 5px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    z-index: 9999;
    font-family: Arial, sans-serif;
">
    <input type="text" id="searchName" placeholder="Rechercher un client" style="width:200px;">
    <div id="dayFilters">
        <label><input type="checkbox" class="filter-day" value="L" checked> L</label>
        <label><input type="checkbox" class="filter-day" value="M" checked> M</label>
        <label><input type="checkbox" class="filter-day" value="W" checked> W</label>
        <label><input type="checkbox" class="filter-day" value="J" checked> J</label>
        <label><input type="checkbox" class="filter-day" value="V" checked> V</label>
        <label><input type="checkbox" class="filter-day" value="S" checked> S</label>
        <label><input type="checkbox" class="filter-day" value="D" checked> D</label>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(html_menu))

# Script JS
js_script = """
<script>

// Tableau des marqueurs
let markers = [];

// Charger les clients depuis l'API
async function loadClients() {
    try {
        const response = await fetch("http://127.0.0.1:5000/clients");
        const data = await response.json();

        data.forEach(c => {
            const m = L.marker([c.latitude, c.longitude], {
                icon: L.AwesomeMarkers.icon({
                    icon: 'info-sign',
                    markerColor: c.couleur || 'blue'
                })
            }).addTo(map_0)
              .bindPopup(`<b>${c.nom_client}</b><br>Code: ${c.code_client}<br>
                          Jours: ${c.jours_livraison}<br>Tournée: ${c.tournee}<br>
                          Adresse: ${c.adresse_complete}`);
            m.nom = c.nom_client;
            m.jours_livraison = c.jours_livraison;
            markers.push(m);
        });

        updateMarkersByDays();
    } catch(err) {
        console.error("Erreur chargement clients:", err);
    }
}

// Filtrage par jours de livraison (logique inversée)
function updateMarkersByDays() {
    const checkedDays = Array.from(document.querySelectorAll('.filter-day:checked'))
                             .map(cb => cb.value);

    markers.forEach(m => {
        // Au moins un jour coché doit être dans les jours du client
        const show = checkedDays.length === 0 || checkedDays.some(day => m.jours_livraison.includes(day));

        if (show) {
            if (!map_0.hasLayer(m)) map_0.addLayer(m);
            if (m._icon) m._icon.classList.add('highlight');
        } else {
            if (map_0.hasLayer(m)) map_0.removeLayer(m);
            if (m._icon) m._icon.classList.remove('highlight');
        }
    });
}

// Auto-suggestion / recherche par nom avec zoom
function searchClient() {
    const value = document.getElementById('searchName').value.toLowerCase();
    if (!value) return;
    markers.forEach(m => {
        if (m.nom.toLowerCase().includes(value)) {
            map_0.setView(m.getLatLng(), 12);
            m.openPopup();
        }
    });
}

// Événements
document.addEventListener("DOMContentLoaded", () => {
    loadClients();

    // Filtre en temps réel
    document.querySelectorAll('.filter-day').forEach(cb => {
        cb.addEventListener('change', updateMarkersByDays);
    });

    // Recherche avec auto-suggestion
    document.getElementById('searchName').addEventListener('input', searchClient);
});

</script>
<style>
.leaflet-marker-icon.highlight {
    filter: drop-shadow(0 0 10px yellow);
    transform: scale(1.2);
    z-index: 9999 !important;
}
</style>
"""

m.get_root().html.add_child(folium.Element(js_script))
m.save("map_clients_postgres_filter_inverted.html")
