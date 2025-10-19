import folium
from folium.plugins import MarkerCluster

# ====== Carte de base ======
m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles="OpenStreetMap")
MarkerCluster(name="Clients").add_to(m)

# (Optionnel) grille repère visuelle
lat_min, lat_max = 49.6, 51
lon_min, lon_max = 1.5, 4
lat_step, lon_step = 0.15, 0.25

def add_grid_cells(map_object):
    lat = lat_min
    while lat < lat_max:
        lon = lon_min
        while lon < lon_max:
            coords = [
                [lat, lon],
                [lat + lat_step, lon],
                [lat + lat_step, lon + lon_step],
                [lat, lon + lon_step],
                [lat, lon],
            ]
            folium.Polygon(coords, color="blue", weight=1, fill=True, fill_opacity=0.08).add_to(map_object)
            lon += lon_step
        lat += lat_step

add_grid_cells(m)

# ====== HTML/CSS/JS embarqués ======
html = r"""
<style>
/* ---------- MENU HAUT ---------- */
#topMenu {
  position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
  background: #1f2937; padding: 12px 25px; border-radius: 12px;
  box-shadow: 2px 2px 12px rgba(0,0,0,0.4); z-index: 9999;
  display: flex; gap: 15px; font-family: 'Segoe UI', system-ui, Arial, sans-serif;
}
#topMenu button {
  width: 200px; height: 48px; font-size: 16px; font-weight: 600;
  background: #2563eb; color: white; border: none; border-radius: 10px; cursor: pointer;
  transition: transform .2s ease, background .2s ease, box-shadow .2s ease;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}
#topMenu button:hover { background: #1d4ed8; transform: translateY(-1px); box-shadow: 0 8px 22px rgba(29,78,216,.35); }

/* ---------- SIDEBAR ---------- */
#sidebar {
  position: fixed; top: 0; right: -440px; width: 420px; height: 100%;
  background: #0b1220; color: #e5e7eb; z-index: 9999;
  box-shadow: -4px 0 18px rgba(0,0,0,0.55); transition: right .35s ease;
  border-left: 1px solid rgba(148,163,184,.12); display: flex; flex-direction: column;
}
#sidebar.open { right: 0; }

#sbHeader { display: flex; align-items: center; justify-content: space-between;
  padding: 16px 18px; border-bottom: 1px solid rgba(148,163,184,.12); }
#sbTitle { font-size: 16px; font-weight: 800; letter-spacing: .02em; color: #93c5fd; }
#closeSidebar { background: transparent; border: none; color: #9ca3af; font-size: 22px; cursor: pointer; }
#closeSidebar:hover { color: #fff; }

#sbTabs { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid rgba(148,163,184,.12); }
.sbTabBtn { padding: 12px 0; text-align: center; cursor: pointer; font-weight: 700; font-size: 14px; color: #9ca3af; background: transparent; border: none; }
.sbTabBtn.active { color: #e5e7eb; background: #0f172a; }

#sbBody { padding: 16px 18px; flex: 1; overflow-y: auto; }
.formRow { display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; }
#sbBody label { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: #9ca3af; }
#sbBody input {
  padding: 10px 12px; font-size: 15px; border-radius: 10px;
  border: 1px solid rgba(148,163,184,.18); background: #0f172a; color: #e5e7eb; outline: none;
}
#sbBody input::placeholder { color: #6b7280; }

.actionsGrid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.btnPrimary, .btnSecondary, .btnDanger {
  padding: 11px 12px; border: none; border-radius: 10px; cursor: pointer; font-size: 15px; font-weight: 700;
}
.btnPrimary { background: #2563eb; color: #fff; } .btnPrimary:hover { background: #1d4ed8; }
.btnSecondary { background: #374151; color: #e5e7eb; } .btnSecondary:hover { background: #4b5563; }
.btnDanger { background: #dc2626; color: #fff; } .btnDanger:hover { background: #b91c1c; }

/* Résultats / Stats */
#resultCounter { margin-top: 4px; font-size: 13px; color: #93c5fd; text-align: center; font-weight: 700; }
#statsCard { margin-top: 8px; background: #0f172a; border: 1px solid rgba(148,163,184,.18);
  border-radius: 12px; padding: 12px; }
#statsLegend { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 6px 10px; margin-top: 8px; font-size: 13px; color: #cbd5e1; }
.legendItem { display: flex; align-items: center; gap: 8px; }
.legendSwatch { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }

/* Autocomplétion */
.suggest-wrap { position: relative; }
#addrSuggest {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0;
  background: #0f172a; border: 1px solid rgba(148,163,184,.18); border-radius: 10px;
  box-shadow: 0 10px 24px rgba(0,0,0,.35); z-index: 10000; display: none; max-height: 220px; overflow: auto;
}
.addr-item { padding: 10px 12px; cursor: pointer; border-bottom: 1px solid rgba(148,163,184,.10); color: #e5e7eb; font-size: 14px; }
.addr-item:hover { background: #111827; }

/* ===== Popup “carte d’identité client” — DARK MODE (sans bordure, croix rouge) ===== */
.marker-popup.advanced {
  background: #0f172a;
  padding: 14px 16px;
  border-radius: 14px;
  box-shadow: 0 6px 22px rgba(0,0,0,0.45);
  width: 290px;
  font-family: 'Segoe UI', system-ui, Arial, sans-serif;
  color: #e5e7eb;
  border: none; /* bord blanc supprimé */
  position: relative;
}
.popup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.popup-title { font-size: 18px; font-weight: 800; color: #93c5fd; line-height: 1.2; }

/* Badge tournée */
.tournee-badge {
  display: inline-block; padding: 4px 10px; font-size: 13px; font-weight: 800; color: #fff;
  border-radius: 20px; text-transform: uppercase; min-width: 50px; text-align: center; letter-spacing: .02em;
  box-shadow: 0 2px 10px rgba(0,0,0,.35);
}

/* Croix de fermeture (gris, survol rouge) */
.popup-close {
  position: absolute;
  top: 10px;
  right: 12px;
  background: transparent;
  border: none;
  color: #9ca3af;      /* gris en normal */
  font-size: 20px;
  cursor: pointer;
  transition: color 0.2s;
}
.popup-close:hover { color: #f87171; } /* rouge au survol */

/* Bloc info sans bordure blanche */
.popup-info {
  background: #0b1220;
  border: none;
  border-radius: 10px;
  padding: 8px 10px;
}
.popup-info .field { margin-bottom: 6px; font-size: 14px; color: #cbd5e1; }
.popup-info .field-label { font-weight: 700; color: #e5e7eb; margin-right: 4px; }

.marker-popup hr { border: none; height: 1px; background: rgba(148,163,184,.18); margin: 12px 0; }

.popup-actions { display: flex; flex-wrap: wrap; gap: 6px; }
.popup-actions .btn {
  flex: 1; padding: 8px 10px; font-size: 14px; font-weight: 800; border: none; border-radius: 8px; cursor: pointer; transition: all .2s ease;
}
.popup-actions .btn-primary { background: #2563eb; color: #fff; } .popup-actions .btn-primary:hover { background: #1d4ed8; transform: translateY(-1px); }
.popup-actions .btn-danger { background: #dc2626; color: #fff; } .popup-actions .btn-danger:hover { background: #b91c1c; transform: translateY(-1px); }
.popup-actions .btn-secondary { background: #374151; color: #e5e7eb; } .popup-actions .btn-secondary:hover { background: #4b5563; transform: translateY(-1px); }
.popup-actions .btn-map { text-align: center; background: #10b981; color: #fff; text-decoration: none; display: inline-block; }
.popup-actions .btn-map:hover { background: #059669; transform: translateY(-1px); }

/* Marqueur visuel */
.client-marker {
  border: 2px solid #fff; width: 36px; height: 36px; border-radius: 50%;
  display: flex; justify-content: center; align-items: center;
  font-weight: 800; font-size: 15px; color: #fff;
  box-shadow: 0 3px 12px rgba(0,0,0,.35); transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.client-marker:hover { transform: scale(1.2); box-shadow: 0 5px 18px rgba(0,0,0,.45); }

/* Sections */
.section { display: none; }
.section.active { display: block; }
</style>

<div id="topMenu">
  <button id="searchBtn">🔍 Recherche client</button>
  <button id="createBtn">➕ Créer client</button>
</div>

<!-- Sidebar -->
<div id="sidebar">
  <div id="sbHeader">
    <div id="sbTitle">Tableau de bord</div>
    <button id="closeSidebar" title="Fermer">✕</button>
  </div>
  <div id="sbTabs">
    <button id="tabSearch" class="sbTabBtn active">Recherche</button>
    <button id="tabForm" class="sbTabBtn">Créer / Modifier</button>
  </div>

  <div id="sbBody">
    <!-- RECHERCHE -->
    <div id="sectionSearch" class="section active">
      <div class="formRow">
        <label for="searchNom">Nom client</label>
        <input type="text" id="searchNom" placeholder="Ex : Dupont">
      </div>
      <div class="formRow">
        <label for="searchCode">Code client</label>
        <input type="text" id="searchCode" placeholder="Ex : 1234">
      </div>
      <div class="formRow">
        <label for="searchJour">Jour(s) (LMWJVSD)</label>
        <input type="text" id="searchJour" placeholder="Ex : LM, JVSD">
      </div>
      <div class="formRow">
        <label for="searchTournee">Tournée (texte)</label>
        <input type="text" id="searchTournee" placeholder="Ex : 1, 2, CODE">
      </div>

      <div class="actionsGrid" style="margin-bottom:8px;">
        <button id="searchBtnApply" class="btnPrimary">Appliquer</button>
        <button id="resetBtn" class="btnSecondary">Réinitialiser</button>
      </div>

      <div id="resultCounter"></div>

      <div id="statsCard">
        <div id="statsHeader" style="display:flex;justify-content:space-between;align-items:center;">
          <div class="title">Répartition par tournée</div>
          <div id="statsTotal">Total: 0</div>
        </div>
        <canvas id="tourPie" width="360" height="220" style="max-height:220px;"></canvas>
        <div id="statsLegend"></div>
      </div>
    </div>

    <!-- FORMULAIRE -->
    <div id="sectionForm" class="section">
      <input type="hidden" id="formId">
      <input type="hidden" id="originalAddress">

      <div class="formRow">
        <label for="cNom">Nom client</label>
        <input type="text" id="cNom" placeholder="Ex : Dupont SA">
      </div>
      <div class="formRow">
        <label for="cCode">Code client</label>
        <input type="number" id="cCode" placeholder="Ex : 1234">
      </div>
      <div class="formRow suggest-wrap">
        <label for="cAdresse">Adresse livraison (obligatoire)</label>
        <input type="text" id="cAdresse" placeholder="Rue, CP, Ville">
        <div id="addrSuggest"></div>
      </div>

      <!-- Lat/Lon optionnelles -->
      <div class="formRow">
        <label for="cLatitude">Latitude (optionnel)</label>
        <input type="text" id="cLatitude" placeholder="Ex : 50.627 (sinon auto par l'API)">
      </div>
      <div class="formRow">
        <label for="cLongitude">Longitude (optionnel)</label>
        <input type="text" id="cLongitude" placeholder="Ex : 3.058 (sinon auto par l'API)">
      </div>

      <div class="formRow">
        <label for="cTournee">Tournée (texte)</label>
        <input type="text" id="cTournee" placeholder="Ex : 1, 2, CODE-A">
      </div>
      <div class="formRow">
        <label for="cJours">Jour(s) (LMWJVSD)</label>
        <input type="text" id="cJours" placeholder="Ex : LM, JVSD">
      </div>

      <div class="actionsGrid">
        <button id="saveClient" class="btnPrimary">Enregistrer</button>
        <button id="cancelClient" class="btnSecondary">Annuler</button>
      </div>
      <div style="margin-top:8px;">
        <button id="deleteClient" class="btnDanger" style="width:100%;">Supprimer ce client</button>
      </div>
    </div>
  </div>
</div>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
/* ===== Global ===== */
let map=null, allClients=[], markers=[], marker_cluster=null;
let tourPieChart=null, editId=null;
let previewMarker=null, previewCircle=null;

/* Couleurs tournées 1..5 (+ Autre) */
const TOUR_COLORS = {1:"rgba(0,123,255,0.85)",2:"rgba(40,167,69,0.85)",3:"rgba(255,193,7,0.9)",4:"rgba(253,126,20,0.9)",5:"rgba(220,53,69,0.9)",0:"rgba(111,66,193,0.85)"};
const TOUR_BORDERS = {1:"rgba(0,123,255,1)",2:"rgba(40,167,69,1)",3:"rgba(255,193,7,1)",4:"rgba(253,126,20,1)",5:"rgba(220,53,69,1)",0:"rgba(111,66,193,1)"};

function getMap(){ for (const k in window) if (k.startsWith("map_")) return window[k]; return null; }
function escapeHtml(s){ return String(s||"").replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }

/* ===== API ===== */
async function fetchClients(params){
  const url = "http://127.0.0.1:5000/clients" + (params ? "?" + params.toString() : "");
  const res = await fetch(url);
  return await res.json();
}
async function createClient(payload){
  return await fetch("http://127.0.0.1:5000/clients", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
}
async function updateClient(id, payload){
  return await fetch(`http://127.0.0.1:5000/clients/${id}`, { method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
}
async function removeClient(id){
  return await fetch(`http://127.0.0.1:5000/clients/${id}`, { method: "DELETE" });
}

/* ===== Recherche / Chargement ===== */
async function loadClients(){
  try{
    const nom = document.getElementById("searchNom").value.trim();
    const code = document.getElementById("searchCode").value.trim();
    const jour = document.getElementById("searchJour").value.trim();
    const tournee = document.getElementById("searchTournee").value.trim();

    const params = new URLSearchParams();
    if(nom) params.append("nom", nom);
    if(code) params.append("code", code);
    if(jour) params.append("jour", jour);
    if(tournee) params.append("tournee", tournee);

    allClients = await fetchClients(params);
    displayMarkers();
    updateStats();
    document.getElementById("resultCounter").innerText = `${allClients.length} client(s) trouvé(s)`;
  }catch(e){ console.error(e); }
}

/* ===== Markers / Cluster (corrigé + nettoyage) ===== */
function displayMarkers() {
  if (!map) map = getMap();

  // Créer une seule fois le cluster
  if (!marker_cluster) {
    marker_cluster = L.markerClusterGroup({ maxClusterRadius: 80, disableClusteringAtZoom: 14 }).addTo(map);
  } else {
    marker_cluster.clearLayers();
  }
  markers = [];

  // Nettoyage coordonnées + filtrage France approx
  const validClients = allClients.filter(c => {
    const latStr = String(c.latitude || "").replace(",", ".").replace(/[^0-9.\-]/g, "");
    const lonStr = String(c.longitude || "").replace(",", ".").replace(/[^0-9.\-]/g, "");
    const lat = parseFloat(latStr);
    const lon = parseFloat(lonStr);
    c.latitude = lat; c.longitude = lon;
    if (isNaN(lat) || isNaN(lon)) return false;
    if (lat < 40 || lat > 52 || lon < -5 || lon > 10) return false;
    return true;
  });

  if (validClients.length === 0) {
    console.warn("⚠️ Aucun client valide à afficher.");
    return;
  }

  validClients.forEach(c => {
    const lat = c.latitude, lon = c.longitude;
    const tRaw = (c.tournee ?? "").toString().trim();
    const tNum = parseInt(tRaw);
    const color = (Number.isInteger(tNum) && tNum>=1 && tNum<=5) ? TOUR_COLORS[tNum] : TOUR_COLORS[0];
    const label = (tRaw.length<=3 ? tRaw : (Number.isInteger(tNum)? String(tNum) : ""));

    const iconHTML = `<div class="client-marker" style="background:${color};">${escapeHtml(label)}</div>`;
    const icon = L.divIcon({ html: iconHTML, className:"", iconSize:[36,36], iconAnchor:[18,18], popupAnchor:[0,-18] });
    const marker = L.marker([lat, lon], { icon }).bindPopup(createPopupHTML(c));
    marker.client = c;
    marker_cluster.addLayer(marker);
    markers.push(marker);
  });

  // Recentrage automatique
  map.invalidateSize();
  setTimeout(() => {
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds(), { padding: [50, 50] });
  }, 100);

  console.log(`📍 ${validClients.length} marqueurs affichés après nettoyage.`);
}

/* ===== Popup “carte d’identité client” — DARK MODE + Itinéraire + Croix ===== */
function createPopupHTML(c) {
  // Nettoyage des données
  const nom = escapeHtml(c.nom_client || "Client inconnu");
  const adresse = escapeHtml(c.adresse_livraison || "Non renseignée");
  const code = escapeHtml(c.code_client || "—");
  const tournee = escapeHtml(c.tournee || "—");
  const jours = escapeHtml(c.jours_livraison || "—");
  const lat = c.latitude ? parseFloat(c.latitude) : null;
  const lon = c.longitude ? parseFloat(c.longitude) : null;

  // Couleur badge tournée
  const tRaw = (c.tournee ?? "").toString().trim();
  const tNum = parseInt(tRaw);
  const badgeColor = (Number.isInteger(tNum) && tNum >= 1 && tNum <= 5) ? TOUR_COLORS[tNum] : TOUR_COLORS[0];

  // Lien Google Maps
  const googleUrl = lat && lon
    ? `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(adresse)}`;

  return `
    <div class="marker-popup advanced">
      <div class="popup-header">
        <div class="popup-title">${nom}</div>
        <span class="tournee-badge" style="background:${badgeColor};">${tournee || "—"}</span>
        <button class="popup-close" onclick="closePopup(this)" title="Fermer">✕</button>
      </div>

      <div class="popup-info">
        <div class="field"><span class="field-label">📍 Adresse :</span> ${adresse}</div>
        <div class="field"><span class="field-label">🏷️ Code client :</span> ${code}</div>
        <div class="field"><span class="field-label">🚚 Tournée :</span> ${tournee}</div>
        <div class="field"><span class="field-label">📅 Jours :</span> ${jours}</div>
      </div>

      <hr>

      <div class="popup-actions">
        <button class="btn btn-primary" onclick="openFormEdit(${c.id})">✏️ Modifier</button>
        <button class="btn btn-danger" onclick="deleteClient(${c.id})">🗑️ Supprimer</button>
        ${lat && lon ? `<button class="btn btn-secondary" onclick="centerOnClient(${lat}, ${lon})">📍 Centrer</button>` : ""}
        <a href="${googleUrl}" target="_blank" class="btn btn-map">🗺️ Itinéraire</a>
      </div>
    </div>
  `;
}

/* Fermer uniquement la popup (sans recentrer) */
function closePopup(btn) {
  const popupEl = btn.closest(".leaflet-popup");
  if (!popupEl) { return; }
  const mapRef = getMap();
  if (mapRef && mapRef.closePopup) mapRef.closePopup();
}

/* Centrage direct depuis la popup */
function centerOnClient(lat, lon) {
  if (!map) return;
  map.setView([lat, lon], 15, { animate: true });
}

/* ===== Stats Chart.js ===== */
function computeTourCounts(){
  const counts = {1:0,2:0,3:0,4:0,5:0, other:0};
  allClients.forEach(c=>{
    const tRaw = (c.tournee ?? "").toString().trim();
    const tNum = parseInt(tRaw);
    if (Number.isInteger(tNum) && tNum >= 1 && tNum <= 5) counts[tNum] += 1;
    else counts.other += 1;
  });
  return counts;
}
function buildLegend(counts){
  const legend = document.getElementById("statsLegend"); legend.innerHTML = "";
  [["Tournée 1",counts[1],TOUR_BORDERS[1]],["Tournée 2",counts[2],TOUR_BORDERS[2]],
   ["Tournée 3",counts[3],TOUR_BORDERS[3]],["Tournée 4",counts[4],TOUR_BORDERS[4]],
   ["Tournée 5",counts[5],TOUR_BORDERS[5]],["Autre",counts.other,TOUR_BORDERS[0]]]
   .forEach(([label,val,color])=>{
     const div=document.createElement("div"); div.className="legendItem";
     const sw=document.createElement("span"); sw.className="legendSwatch"; sw.style.background=color;
     const txt=document.createElement("span"); txt.textContent=`${label}: ${val}`;
     div.appendChild(sw); div.appendChild(txt); legend.appendChild(div);
   });
}
function updateStats(){
  const counts = computeTourCounts();
  const data = [counts[1],counts[2],counts[3],counts[4],counts[5],counts.other];
  const bg = [TOUR_COLORS[1],TOUR_COLORS[2],TOUR_COLORS[3],TOUR_COLORS[4],TOUR_COLORS[5],TOUR_COLORS[0]];
  const br = [TOUR_BORDERS[1],TOUR_BORDERS[2],TOUR_BORDERS[3],TOUR_BORDERS[4],TOUR_BORDERS[5],TOUR_BORDERS[0]];
  const total = data.reduce((a,b)=>a+b,0);
  document.getElementById("statsTotal").textContent = "Total: " + total;

  buildLegend(counts);
  const ctx = document.getElementById("tourPie").getContext("2d");
  const cfg = {
    type: 'pie',
    data: { labels: ["1","2","3","4","5","Autre"], datasets: [{ data, backgroundColor: bg, borderColor: br, borderWidth: 2 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false },
      tooltip: { callbacks: { label: (ctx)=> { const v=ctx.parsed||0; const pct = total? Math.round(v*100/total):0; const lab = ctx.label==="Autre"?"Autre":"Tournée "+ctx.label; return `${lab}: ${v} (${pct}%)`; } } } } }
  };
  if(tourPieChart){ tourPieChart.data.datasets[0].data = data; tourPieChart.update(); }
  else { tourPieChart = new Chart(ctx, cfg); }
}

/* ===== Formulaire ===== */
function switchTab(tab){
  document.getElementById("tabSearch").classList.toggle("active", tab==="search");
  document.getElementById("tabForm").classList.toggle("active", tab==="form");
  document.getElementById("sectionSearch").classList.toggle("active", tab==="search");
  document.getElementById("sectionForm").classList.toggle("active", tab==="form");
  document.getElementById("sbTitle").textContent = tab==="search" ? "Recherche" : (editId? "Modifier client" : "Créer client");
}
function clearForm(){
  editId = null;
  document.getElementById("formId").value = "";
  document.getElementById("originalAddress").value = "";
  document.getElementById("cNom").value = "";
  document.getElementById("cCode").value = "";
  document.getElementById("cAdresse").value = "";
  document.getElementById("cLatitude").value = "";
  document.getElementById("cLongitude").value = "";
  document.getElementById("cTournee").value = "";
  document.getElementById("cJours").value = "";
  document.getElementById("deleteClient").disabled = true;
  hideAddrSuggest();
}
function fillForm(c){
  editId = c.id;
  document.getElementById("formId").value = c.id;
  document.getElementById("originalAddress").value = c.adresse_livraison || "";
  document.getElementById("cNom").value = c.nom_client || "";
  document.getElementById("cCode").value = c.code_client || "";
  document.getElementById("cAdresse").value = c.adresse_livraison || "";
  document.getElementById("cLatitude").value = (c.latitude ?? "");
  document.getElementById("cLongitude").value = (c.longitude ?? "");
  document.getElementById("cTournee").value = c.tournee || "";
  document.getElementById("cJours").value = c.jours_livraison || "";
  document.getElementById("deleteClient").disabled = false;
  hideAddrSuggest();

  if(c.latitude != null && c.longitude != null){ previewLocation(c.latitude, c.longitude); }
}
function openSidebar(){ document.getElementById("sidebar").classList.add("open"); }
function closeSidebar(){ document.getElementById("sidebar").classList.remove("open"); }
function openFormCreate(){ openSidebar(); switchTab("form"); clearForm(); }
function openFormEdit(id){ const c = allClients.find(x=>x.id===id); if(!c) return; openSidebar(); switchTab("form"); fillForm(c); }

/* Sauvegarde (API géocode si lat/lon vides) */
async function saveClient(){
  const nom = document.getElementById("cNom").value.trim();
  const code_client = parseInt(document.getElementById("cCode").value) || null;
  const adresse = document.getElementById("cAdresse").value.trim();
  const lat = document.getElementById("cLatitude").value.trim();
  const lon = document.getElementById("cLongitude").value.trim();
  const tournee = document.getElementById("cTournee").value.trim();
  const jours = document.getElementById("cJours").value.trim();

  if(!nom){ alert("Nom client obligatoire."); return; }
  if(!code_client){ alert("Code client obligatoire."); return; }
  if(!adresse){ alert("Adresse livraison obligatoire."); return; }

  const payload = {
    nom_client: nom,
    code_client: code_client,
    adresse_livraison: adresse,
    latitude: lat || undefined,
    longitude: lon || undefined,
    tournee: tournee,
    jours_livraison: jours
  };

  try{
    if(editId){ await updateClient(editId, payload); }
    else { await createClient(payload); }
    await loadClients();
    switchTab("search");
  }catch(e){ console.error(e); alert("Erreur lors de l'enregistrement."); }
}

async function deleteClient(id){
  if(!(id||editId)) return;
  const toDelete = id || editId;
  if(!confirm("Supprimer ce client ?")) return;
  try{ await removeClient(toDelete); if(toDelete===editId){ clearForm(); switchTab("search"); } await loadClients(); }
  catch(e){ console.error(e); alert("Erreur lors de la suppression."); }
}

/* ===== Autocomplétion Nominatim ===== */
let addrDebounceTimer = null;
async function queryNominatimSuggest(q){
  const url = "https://nominatim.openstreetmap.org/search?format=json&countrycodes=fr&accept-language=fr&viewbox=-1.5,51.5,5.0,48.5&bounded=1&limit=8&q="+encodeURIComponent(q);
  const res=await fetch(url,{headers:{"Accept":"application/json"}});
  return res.ok?await res.json():[];
}
function hideAddrSuggest(){ const box = document.getElementById("addrSuggest"); box.style.display="none"; box.innerHTML=""; }
function showAddrSuggest(items){
  const box = document.getElementById("addrSuggest");
  if(!items || items.length===0){ hideAddrSuggest(); return; }
  box.innerHTML = items.map(it=>`<div class="addr-item" data-lat="${it.lat}" data-lon="${it.lon}" data-label="${escapeHtml(it.display_name||"")}">${escapeHtml(it.display_name||"")}</div>`).join("");
  box.style.display="block";
  Array.from(box.querySelectorAll(".addr-item")).forEach(el=>{
    el.addEventListener("click", ()=>{
      const addr = el.getAttribute("data-label");
      const lat = el.getAttribute("data-lat");
      const lon = el.getAttribute("data-lon");
      document.getElementById("cAdresse").value = addr;
      document.getElementById("cLatitude").value = lat;
      document.getElementById("cLongitude").value = lon;
      document.getElementById("originalAddress").value = addr;
      hideAddrSuggest();
      previewLocation(lat, lon);
    });
  });
}
function onAddrInput(e){
  const q = e.target.value.trim();
  if(addrDebounceTimer) clearTimeout(addrDebounceTimer);
  if(!q){ hideAddrSuggest(); return; }
  addrDebounceTimer = setTimeout(async ()=>{ try{ showAddrSuggest(await queryNominatimSuggest(q)); }catch(err){ console.error(err); } }, 350);
}

/* ===== Preview centrage ===== */
function previewLocation(lat, lon){
  if(!map) return;
  const latNum = parseFloat(String(lat).replace(",", "."));
  const lonNum = parseFloat(String(lon).replace(",", "."));
  if(isNaN(latNum)||isNaN(lonNum)) return;
  if(previewMarker){ map.removeLayer(previewMarker); }
  if(previewCircle){ map.removeLayer(previewCircle); }
  previewMarker = L.marker([latNum, lonNum]).addTo(map);
  previewCircle = L.circle([latNum, lonNum], { radius: 120, weight: 1, opacity: .9, fillOpacity: .1 }).addTo(map);
  map.setView([latNum, lonNum], 14);
}

/* ===== Init ===== */
document.addEventListener("DOMContentLoaded", ()=>{
  map = getMap();

  // cluster créé UNE SEULE fois
  marker_cluster = L.markerClusterGroup({ maxClusterRadius: 80, disableClusteringAtZoom: 14 }).addTo(map);

  loadClients();

  // Sidebar / onglets
  document.getElementById("searchBtn").onclick=()=>{ document.getElementById("sidebar").classList.add("open"); switchTab("search"); };
  document.getElementById("createBtn").onclick=()=>{ document.getElementById("sidebar").classList.add("open"); openFormCreate(); };
  document.getElementById("closeSidebar").onclick=()=>{ document.getElementById("sidebar").classList.remove("open"); };

  document.getElementById("tabSearch").onclick=()=>switchTab("search");
  document.getElementById("tabForm").onclick=()=>switchTab("form");

  // Recherche live
  ["searchNom","searchCode","searchJour","searchTournee"].forEach(id=>{
    document.getElementById(id).addEventListener("input", loadClients);
    document.getElementById(id).addEventListener("change", loadClients);
  });
  document.getElementById("searchBtnApply").onclick=loadClients;
  document.getElementById("resetBtn").onclick=()=>{ ["searchNom","searchCode","searchJour","searchTournee"].forEach(id=>document.getElementById(id).value=""); loadClients(); };

  // Formulaire
  document.getElementById("saveClient").onclick=saveClient;
  document.getElementById("cancelClient").onclick=()=>{ clearForm(); switchTab("search"); };
  document.getElementById("deleteClient").onclick=()=>deleteClient();
  document.getElementById("deleteClient").disabled = true;

  // Autocomplétion adresse
  const addr = document.getElementById("cAdresse");
  addr.addEventListener("input", onAddrInput);
  addr.addEventListener("focus", (e)=>{ if(e.target.value.trim()) onAddrInput(e); });
  addr.addEventListener("blur", ()=>{ setTimeout(hideAddrSuggest, 200); }); // laisse le temps de cliquer
});
</script>
"""

m.get_root().html.add_child(folium.Element(html))
m.save("index.html")
print("✅ Dashboard généré -> index.html (popup dark sans bordure, croix rouge, cluster corrigé)")
