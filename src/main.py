import folium
from folium.plugins import MarkerCluster

m = folium.Map(location=[50.6,3.0], zoom_start=7, tiles="OpenStreetMap")
marker_cluster = MarkerCluster(name="Clients").add_to(m)

# Grille
lat_min, lat_max = 49.6, 51
lon_min, lon_max = 1.5, 4
lat_step, lon_step = 0.15, 0.25
def add_grid_cells(map_object):
    lat=lat_min
    while lat<lat_max:
        lon=lon_min
        while lon<lon_max:
            coords=[[lat,lon],[lat+lat_step,lon],[lat+lat_step,lon+lon_step],[lat,lon+lon_step],[lat,lon]]
            folium.Polygon(coords, color="blue", weight=1, fill=True, fill_opacity=0.1).add_to(map_object)
            lon+=lon_step
        lat+=lat_step
add_grid_cells(m)

# HTML + JS
html=r"""
<style>
#topMenu{
    position:fixed;
    top:10px;
    left:50%;
    transform:translateX(-50%);
    background:white;padding:12px 25px;
    border-radius:12px;
    box-shadow:2px 2px 10px rgba(0,0,0,0.25);
    z-index:9999;
    display:flex;
    gap:15px;
    font-family:Arial,sans-serif;
}

#topMenu button{
    width:180px;
    height:45px;
    font-size:15px;
    font-weight:bold;
    background:#007bff;
    color:white;
    border:none;
    border-radius:8px;
    cursor:pointer;
    text-align:center;
    transition:all 0.25s ease;
}

#topMenu button:hover{
    background:#0056b3;
    transform:scale(1.05);
}

.marker-popup{
    font-family:Arial,sans-serif;
    font-size:13px;
    line-height:1.4;
    width:270px;
}

.marker-popup b{
    font-size:16px;
    color:#007bff;
}

.marker-popup .btn{
    display:inline-block;
    margin-top:6px;
    margin-right:5px;
    padding:5px 10px;
    font-size:14px;
    font-weight:bold;
    color:white;
    background-color:#007bff;
    border:none;
    border-radius:6px;
    cursor:pointer;
    transition:0.2s;
}

.marker-popup .btn:hover{
    background-color:#0056b3;
}

.client-marker{
    border:2px solid rgb(173, 215, 255);
    width:30px;height:30px;
    border-radius:50%;
    display:flex;
    justify-content:center;
    align-items:center;
    font-weight:bold;
    font-size:14px;
    color:white;
}

.client-marker:hover{
    transform:scale(1.15);
    transition:0.2s;
}

#searchBox,#formClient{
    position:fixed;
    top:80px;
    right:20px;
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:2px 2px 10px rgba(0,0,0,0.25);
    z-index:9999;
    display:none;
    flex-direction:column;
    gap:10px;
    width:320px;
    font-family:Arial,sans-serif;
}

#formClient input{
    padding:6px;
    border-radius:6px;
    border:1px solid #ccc;
}

#formClient button{
    padding:8px;
    border-radius:6px;
    border:none;background:#007bff;
    color:white;
    cursor:pointer;
}
 
#formClient button:hover{  
    background:#0056b3;
}

#resultCounter{
    font-size:14px;
    color:#007bff;
    margin-top:5px;
}

</style>

<div id="topMenu">
<button id="searchBtn">🔍 Recherche client</button>
<button id="createBtn">➕ Créer client</button>
</div>

<div id="searchBox">
<input type="text" id="searchNom" placeholder="Nom client">
<input type="text" id="searchCode" placeholder="Code client">
<input type="text" id="searchJour" placeholder="Jour livraison">
<input type="text" id="searchTournee" placeholder="Tournée">
<div id="resultCounter"></div>
</div>

<div id="formClient">
<h3 id="formTitle">Créer client</h3>
<input type="text" id="cNom" placeholder="Nom client">
<input type="number" id="cCode" placeholder="Code client">
<input type="text" id="cAdresse" placeholder="Adresse livraison">
<input type="text" id="cLatitude" placeholder="Latitude">
<input type="text" id="cLongitude" placeholder="Longitude">
<input type="number" id="cTournee" placeholder="Tournée">
<input type="text" id="cJours" placeholder="Jours livraison">
<button id="saveClient">Enregistrer</button>
<button id="cancelClient" style="background:#6c757d;">Annuler</button>
</div>

<script>
var map=null, markers=[], allClients=[], editId=null, marker_cluster=null, cluster_radius= 20000;

function getMap(){for(var k in window) if(k.startsWith("map_")) return window[k]; return null;}

async function loadClients(){
    try{const res=await fetch("http://127.0.0.1:5000/clients"); allClients=await res.json(); displayMarkers();}catch(e){console.error(e);}
}

function createPopupHTML(c){
    return `<div class='marker-popup'><b>${c.nom_client}</b><br>Code: ${c.code_client}<br>Adresse: ${c.adresse_complete||"Non renseignée"}<br>Jours: ${c.jours_livraison||"Non renseigné"}<br>Tournée: ${c.tournee||0}<br><button class='btn' onclick="editClient(${c.id})">Modifier</button><button class='btn' onclick="deleteClient(${c.id})">Supprimer</button></div>`;
}

function displayMarkers(){
    if(!map) map=getMap();
    if(marker_cluster) marker_cluster.clearLayers();
    else marker_cluster=L.markerClusterGroup({ maxClusterRadius: cluster_radius }).addTo(map);
    markers=[];

    allClients.forEach(c=>{
        const lat=parseFloat(c.latitude); const lon=parseFloat(c.longitude); if(isNaN(lat)||isNaN(lon)) return;
        const tournee=parseInt(c.tournee)||0;

        let color="rgba(0,123,255,0.6)";
        switch(tournee){
            case 1: color="rgba(0,123,255,0.6)"; break;
            case 2: color="rgba(40,167,69,0.6)"; break;
            case 3: color="rgba(255,193,7,0.6)"; break;
            case 4: color="rgba(253,126,20,0.6)"; break;
            case 5: color="rgba(220,53,69,0.6)"; break;
        }

        const iconHTML=`<div class="client-marker" style="background:${color};">${tournee>0?tournee:""}</div>`;
        const icon=L.divIcon({html:iconHTML,className:"",iconSize:[36,36],iconAnchor:[18,18],popupAnchor:[0,-18]});
        const marker=L.marker([lat,lon],{icon}).bindPopup(createPopupHTML(c));
        marker.client=c; marker_cluster.addLayer(marker); markers.push(marker);
    });
}

document.addEventListener("DOMContentLoaded",()=>{
    map=getMap(); marker_cluster=L.markerClusterGroup().addTo(map); loadClients();
    document.getElementById("searchBtn").onclick=()=>{const s=document.getElementById("searchBox"); s.style.display=(s.style.display==="flex")?"none":"flex";};
    document.getElementById("createBtn").onclick=()=>showForm();
    document.getElementById("cancelClient").onclick=()=>hideForm();
    document.getElementById("saveClient").onclick=saveClient;
});

function showForm(client=null){
    editId=client?.id||null;
    document.getElementById("formTitle").innerText=editId?"Modifier client":"Créer client";
    document.getElementById("cNom").value=client?.nom_client||"";
    document.getElementById("cCode").value=client?.code_client||"";
    document.getElementById("cAdresse").value=client?.adresse_complete||"";
    document.getElementById("cLatitude").value=client?.latitude||"";
    document.getElementById("cLongitude").value=client?.longitude||"";
    document.getElementById("cTournee").value=client?.tournee||"";
    document.getElementById("cJours").value=client?.jours_livraison||"";
    document.getElementById("formClient").style.display="flex";
}
function hideForm(){editId=null; document.getElementById("formClient").style.display="none";}

async function saveClient(){
    const data={nom_client:document.getElementById("cNom").value.trim(),
                code_client:parseInt(document.getElementById("cCode").value),
                adresse_complete:document.getElementById("cAdresse").value.trim(),
                latitude:document.getElementById("cLatitude").value.trim(),
                longitude:document.getElementById("cLongitude").value.trim(),
                tournee:parseInt(document.getElementById("cTournee").value),
                jours_livraison:document.getElementById("cJours").value.trim()};
    const url=editId?`http://127.0.0.1:5000/clients/${editId}`:"http://127.0.0.1:5000/clients";
    const method=editId?"PUT":"POST";
    await fetch(url,{method,headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
    hideForm(); loadClients();
}

async function deleteClient(id){if(!confirm("Supprimer ce client ?")) return; await fetch(`http://127.0.0.1:5000/clients/${id}`,{method:"DELETE"}); loadClients();}
function editClient(id){const c=allClients.find(x=>x.id===id); if(c) showForm(c);}
</script>
"""

m.get_root().html.add_child(folium.Element(html))
m.save("index.html")
print("✅ Dashboard prêt")