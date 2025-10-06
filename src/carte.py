import folium

# Carte principale
m = folium.Map(location=[48.85, 2.35], zoom_start=6, tiles="OpenStreetMap")

# JavaScript
js_script = """
<script>

// Fonction pour charger les clients depuis la base
async function loadClients() {
    const response = await fetch('http://127.0.0.1:5000/clients');
    const clients = await response.json();

    clients.forEach(c => {
        L.marker([c.latitude, c.longitude], {
            icon: L.AwesomeMarkers.icon({
                icon: 'info-sign',
                markerColor: c.couleur || 'blue'
            })
        })
        .addTo(map_0)
        .bindPopup(`<b>${c.nom_client}</b><br>
                    Code: ${c.code_client}<br>
                    Jours: ${c.jours_livraison}<br>
                    Tournée: ${c.tournee}<br>
                    Adresse: ${c.adresse_complete}`);
    });
}

// Fonction appelée au clic sur la carte
function onMapClick(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;

    const formHtml = `
        <div style="width:200px">
            <h4>Créer un client</h4>
            <input id="code_client" placeholder="Code client" style="width:100%;"><br>
            <input id="nom_client" placeholder="Nom client" style="width:100%;"><br>
            <input id="jours_livraison" placeholder="Jours (ex: LMV)" style="width:100%;"><br>
            <input id="adresse_complete" placeholder="Adresse complète" style="width:100%;"><br>
            <input id="couleur" placeholder="Couleur" style="width:100%;"><br>
            <input id="tournee" type="number" placeholder="Tournée" style="width:100%;"><br>
            <button onclick="saveClient(${lat}, ${lon})">Enregistrer</button>
        </div>
    `;

    L.popup()
        .setLatLng(e.latlng)
        .setContent(formHtml)
        .openOn(map_0);
}

// Envoi du client au backend
async function saveClient(lat, lon) {
    const client = {
        code_client: document.getElementById("code_client").value,
        nom_client: document.getElementById("nom_client").value,
        jours_livraison: document.getElementById("jours_livraison").value,
        adresse_complete: document.getElementById("adresse_complete").value,
        couleur: document.getElementById("couleur").value || "blue",
        tournee: parseInt(document.getElementById("tournee").value) || 0,
        latitude: lat,
        longitude: lon
    };

    const res = await fetch("http://127.0.0.1:5000/clients", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(client)
    });

    if (res.ok) {
        alert("✅ Client ajouté !");
        location.reload();
    } else {
        alert("❌ Erreur lors de l'ajout du client !");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadClients();
    map_0.on('click', onMapClick);
});

</script>
"""

m.get_root().html.add_child(folium.Element(js_script))
m.save("index.html")
