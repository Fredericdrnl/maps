import folium
from folium.plugins import MarkerCluster

# Carte sans tuile par défaut (on bascule clair/sombre côté JS)
m = folium.Map(location=[50.6, 3.0], zoom_start=7, tiles=None, control_scale=False)

# Un cluster Folium pour initialiser (on le gérera côté JS)
MarkerCluster(name="Clients").add_to(m)

# (Optionnel) grille simple pour le nord de la France
lat_min, lat_max = 49.6, 51.0
lon_min, lon_max = 1.5, 4.0
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
            folium.Polygon(coords, color="blue", weight=1, fill=True, fill_opacity=0.05).add_to(map_object)
            lon += lon_step
        lat += lat_step
add_grid_cells(m)

html = r"""
<style>
/* =================== Thèmes =================== */
:root{
  --bg: #ffffff;
  --bg-elev: #f7f7f9;
  --panel: #ffffff;
  --text: #0f172a;
  --muted: #6b7280;
  --primary: #2563eb;
  --border: rgba(15,23,42,.12);
  --accent: #2563eb;
  --success: #10b981;
  --danger: #dc2626;
  --blue-soft: rgba(59,130,246,.15);
  --shadow: 0 8px 24px rgba(0,0,0,.12);
  --scroll-track: rgba(15,23,42,.06);
  --scroll-thumb: rgba(15,23,42,.25);
}
body.dark{
  --bg: #0b1220;
  --bg-elev: #0f172a;
  --panel: #0f172a;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --primary: #3b82f6;
  --border: rgba(148,163,184,.2);
  --accent: #93c5fd;
  --success: #10b981;
  --danger: #ef4444;
  --blue-soft: rgba(59,130,246,.18);
  --shadow: 0 10px 28px rgba(0,0,0,.45);
  --scroll-track: rgba(148,163,184,.08);
  --scroll-thumb: rgba(148,163,184,.35);
}
* { transition: background-color .25s ease, color .25s ease, border-color .25s ease; }

/* =================== Scrollbars =================== */
.leftMenu, #sidebarRight, #editPanel, #legendDrawer {
  scrollbar-width: thin;
  scrollbar-color: var(--scroll-thumb) var(--scroll-track);
}
.leftMenu::-webkit-scrollbar, #sidebarRight::-webkit-scrollbar, #editPanel::-webkit-scrollbar, #legendDrawer::-webkit-scrollbar{
  width: 10px; height: 10px;
}
.leftMenu::-webkit-scrollbar-track, #sidebarRight::-webkit-scrollbar-track, #editPanel::-webkit-scrollbar-track, #legendDrawer::-webkit-scrollbar-track{
  background: var(--scroll-track); border-radius: 10px;
}
.leftMenu::-webkit-scrollbar-thumb, #sidebarRight::-webkit-scrollbar-thumb, #editPanel::-webkit-scrollbar-thumb, #legendDrawer::-webkit-scrollbar-thumb{
  background: var(--scroll-thumb); border-radius: 10px; border: 2px solid transparent; background-clip: padding-box;
}
.leftMenu::-webkit-scrollbar-thumb:hover, #sidebarRight::-webkit-scrollbar-thumb:hover, #editPanel::-webkit-scrollbar-thumb:hover, #legendDrawer::-webkit-scrollbar-thumb:hover{
  background: rgba(99,102,241,.6);
}

/* =================== Menu latéral ouvrable (gauche) =================== */
#leftMenuToggle{
  position: fixed; top: 12px; left: 12px; z-index: 10001;
  background: var(--panel); border: 1px solid var(--border); color: var(--text);
  padding: 8px 12px; border-radius: 10px; cursor: pointer; box-shadow: var(--shadow);
  font-weight: 900; font-size: 13px;
}
.leftMenu{
  position: fixed; top: 0; left: -360px; width: 340px; height: 100%;
  background: var(--panel); color: var(--text); z-index: 10000; box-shadow: 4px 0 18px rgba(0,0,0,.35);
  border-right: 1px solid var(--border); transition: left .3s ease; display:flex; flex-direction: column;
}
.leftMenu.open{ left: 0; }
.leftMenuHeader{ display:flex; justify-content:space-between; align-items:center; padding: 12px 14px; border-bottom:1px solid var(--border); }
.leftMenuTitle{ font-weight:900; color: var(--accent); }
.leftMenuClose{ background: transparent; border: none; color: var(--muted); font-size: 20px; cursor: pointer; }
.leftMenuBody{ padding: 12px 14px; overflow:auto; display:flex; flex-direction:column; gap:10px; }
.formRow{ display:flex; flex-direction:column; gap:6px; }
.leftMenuBody label{ font-size: 11px; text-transform: uppercase; letter-spacing:.06em; color: var(--muted); }
.leftMenuBody input{
  padding: 10px 12px; font-size: 14px; border-radius: 10px; border:1px solid var(--border); background: var(--bg-elev); color: var(--text);
}
.actionsGrid{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.btnPrimary,.btnSecondary{ padding: 10px 12px; border-radius: 10px; border:none; cursor:pointer; font-weight:800; font-size:14px; }
.btnPrimary{ background: var(--primary); color:#fff; } .btnSecondary{ background:#374151; color:#e5e7eb; }

/* =================== Boutons bas-gauche : Légende + Thème =================== */
#legendActionBar{
  position: fixed; left: 12px; bottom: 12px; z-index: 9999; display:flex; gap:8px;
}
.actionBtn{
  width: 44px; height: 44px; border-radius: 12px; display:flex; align-items:center; justify-content:center;
  background: var(--panel); color: var(--text); border:1px solid var(--border); box-shadow: var(--shadow); font-size: 20px; font-weight:900; cursor:pointer;
}

/* Drawer Légende */
#legendDrawer{
  position: fixed; left: 12px; bottom: 68px; z-index: 9999;
  min-width: 280px; max-width: 340px; max-height: 52vh; overflow: auto;
  background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow);
  transform: translateY(8px); opacity: 0; pointer-events: none; transition: opacity .2s ease, transform .2s ease;
}
#legendDrawer.open{ transform: translateY(0); opacity: 1; pointer-events: auto; }
#legendHeader { display:grid; grid-template-columns: 1fr auto auto auto; gap: 8px; align-items:center; padding: 10px 12px; border-bottom: 1px solid var(--border);}
#legendHeader h4{ margin:0; font-size: 13px; color: var(--accent); }
#legendFilterBadge, #legendTotal{ display:none; font-size: 12px; padding: 3px 8px; border-radius: 999px; border: 1px solid var(--border); background: var(--bg-elev); }
#legendClearBtn, #legendExportBtn { padding: 6px 8px; font-size: 12px; font-weight: 800; background: #374151; color: #e5e7eb; border: none; border-radius: 8px; cursor: pointer; }
#tourLegendBody{ padding: 6px 12px 10px; }
.legendRow{
  display:grid; grid-template-columns: 14px 1fr auto; gap:8px; align-items:center;
  font-size: 13px; padding: 6px 8px; border-bottom: 1px dashed var(--border); cursor: pointer; border-radius: 8px;
}
.legendRow:last-child{ border-bottom:none; }
.legendRow.active{ background: var(--blue-soft); }
.legendSw{ width:14px; height:14px; border-radius:4px; }
.legendLabel{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; text-transform: uppercase; }
.legendCount{ color: var(--muted); font-variant-numeric: tabular-nums; }

/* =================== Sidebar DROITE : Création + (style partagé) =================== */
#sidebarRight {
  position: fixed; top: 0; right: -440px; width: 420px; height: 100%;
  background: var(--panel); color: var(--text); z-index: 9998;
  box-shadow: -4px 0 18px rgba(0,0,0,0.35); transition: right .35s ease;
  border-left: 1px solid var(--border); display: flex; flex-direction: column;
}
#sidebarRight.open { right: 0; }
.sbHeader { display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-bottom: 1px solid var(--border); }
.sbTitle { font-size: 15px; font-weight: 900; letter-spacing: .02em; color: var(--accent); }
.sbClose { background: transparent; border: none; color: var(--muted); font-size: 20px; cursor: pointer; }
.sbTabs { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid var(--border); }
.sbTabBtn { padding: 10px 0; background: transparent; border: none; cursor: pointer; font-weight: 900; color: var(--muted); font-size: 13px; }
.sbTabBtn.active{ color: var(--text); background: var(--bg-elev); }

.sbBody{ padding: 12px 14px; flex: 1; overflow-y: auto; }
.sbBody label{ font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.sbBody input{
  padding: 10px 12px; font-size: 14px; border-radius: 10px; border: 1px solid var(--border);
  background: var(--bg-elev); color: var(--text); outline: none;
}
.btnPrimary,.btnSecondary,.btnDanger{ padding: 10px 12px; border: none; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 800; }
.btnPrimary{ background: var(--primary); color: #fff; } .btnSecondary{ background: #374151; color: #e5e7eb; } .btnDanger{ background: var(--danger); color:#fff; }

/* =================== Panneau MODIFIER (droite) =================== */
#editPanel{
  position: fixed; top: 0; right: -440px; width: 420px; height: 100%;
  background: var(--panel); color: var(--text); z-index: 9999; box-shadow: -4px 0 18px rgba(0,0,0,.35);
  transition: right .35s ease; border-left: 1px solid var(--border); display:flex; flex-direction: column;
}
#editPanel.open{ right: 0; }
#editHeader{ display:flex; align-items:center; justify-content:space-between; padding: 12px 14px; border-bottom:1px solid var(--border); }
#editTitle{ font-weight:900; color: var(--accent); font-size: 15px; }
#closeEdit{ background: transparent; border:none; color: var(--muted); font-size: 20px; cursor:pointer; }
#editBody{ padding: 12px 14px; flex:1; overflow:auto; }
#editBody .formRow input{ background: var(--bg-elev); color: var(--text); border:1px solid var(--border); }
#editActions{ padding: 10px 14px; border-top:1px solid var(--border); display:flex; gap:8px; }

/* =================== Popups =================== */
.marker-popup.advanced{
  background: var(--panel);
  padding: 12px 14px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  width: 300px;
  font-family: system-ui, -apple-system, Segoe UI, Arial;
  color: var(--text);
  border: 1px solid var(--border);
  position: relative;
}
.popup-header{ display:flex; justify-content: space-between; align-items:flex-start; margin-bottom: 8px; gap: 8px; }
.popup-title{ font-size: 17px; font-weight: 900; color: var(--text); line-height:1.1; }
.tournee-badge{ display:inline-block; padding:4px 10px; font-size: 12px; font-weight: 900; color:#fff; border-radius: 20px; text-transform: uppercase; background: #a855f7; } /* badge sans croix */
.popup-close{ position:absolute; top:8px; right:10px; background:none; border:none; color: var(--muted); font-size:18px; cursor:pointer; }
.popup-close:hover{ color: var(--danger); }
.popup-info{ background: var(--bg-elev); border-radius: 10px; padding: 8px 10px; border:1px solid var(--border); }
.popup-info .field{ margin-bottom:6px; font-size:14px; color: var(--text); }
.popup-info .field-label{ font-weight:800; margin-right:4px; }
.marker-popup hr{ border:none; height:1px; background: var(--border); margin: 10px 0; }
.popup-actions{ display:flex; gap:6px; flex-wrap: wrap; }
.popup-actions .btn{ flex:1; padding: 8px 10px; border-radius: 8px; border:none; cursor:pointer; font-weight:800; font-size: 14px; }
.btn-map{ background: var(--success); color:#fff; } .btn-primary{ background: var(--primary); color:#fff; } .btn-danger{ background: var(--danger); color:#fff; } .btn-secondary{ background:#374151; color:#e5e7eb; }

/* =================== Marqueurs & Clusters (typo homogène) =================== */
.client-marker{
  border:0; width:28px; height:28px; border-radius:50%;
  display:flex; justify-content:center; align-items:center;
  font-weight: 900; font-size: 10px; color:#fff; text-transform: uppercase; letter-spacing:.02em;
  box-shadow: 0 3px 12px rgba(0,0,0,.35); padding:0 2px; line-height:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.leaflet-marker-icon .marker-cluster-count,
.marker-cluster div span{
  font-weight: 900 !important;
  font-size: 10px !important;
  text-transform: uppercase !important;
  color: #fff !important;
}

/* Retirer le chrome natif Leaflet pour popup + contrôles zoom */
.leaflet-popup-content-wrapper, .leaflet-popup, .leaflet-popup-tip{ background: transparent !important; border:none !important; box-shadow:none !important; }
.leaflet-popup-content{ margin:0 !important; padding:0 !important; }
.leaflet-control-zoom{ display:none !important; } /* ⬅ enlève + / − */
</style>

<!-- Menu latéral ouvrable (gauche) -->
<button id="leftMenuToggle">☰ Menu</button>
<aside id="leftMenu" class="leftMenu">
  <div class="leftMenuHeader">
    <div class="leftMenuTitle">Tableau de bord</div>
    <button class="leftMenuClose" id="leftMenuClose">✕</button>
  </div>
  <div class="leftMenuBody">
    <div class="formRow"><label for="searchNom">Nom client</label><input type="text" id="searchNom" placeholder="Ex : Dupont"></div>
    <div class="formRow"><label for="searchCode">Code client</label><input type="text" id="searchCode" placeholder="Ex : 1234"></div>
    <div class="formRow"><label for="searchJour">Jour(s) (LMWJVSD)</label><input type="text" id="searchJour" placeholder="Ex : LM, JVSD"></div>
    <div class="formRow"><label for="searchTournee">Tournée</label><input type="text" id="searchTournee" placeholder="Ex : T020, FOUR, 1, 2"></div>
    <div class="actionsGrid">
      <button id="searchBtnApply" class="btnPrimary">Appliquer</button>
      <button id="resetBtn" class="btnSecondary">Réinitialiser</button>
    </div>
    <div id="resultCounter" style="font-weight:800; color:var(--accent); text-align:center;"></div>

    <hr style="border:none;height:1px;background:var(--border); margin:10px 0;">

    <div class="formRow"><label for="cNom">Nom client</label><input type="text" id="cNom" placeholder="Ex : Dupont SA"></div>
    <div class="formRow"><label for="cCode">Code client</label><input type="number" id="cCode" placeholder="Ex : 1234"></div>
    <div class="formRow"><label for="cAdresse">Adresse livraison (obligatoire)</label><input type="text" id="cAdresse" placeholder="Rue, CP, Ville"></div>
    <div class="formRow"><label for="cLatitude">Latitude (optionnel)</label><input type="text" id="cLatitude" placeholder="Ex : 50.627"></div>
    <div class="formRow"><label for="cLongitude">Longitude (optionnel)</label><input type="text" id="cLongitude" placeholder="Ex : 3.058"></div>
    <div class="formRow"><label for="cTournee">Tournée</label><input type="text" id="cTournee" placeholder="Ex : T020, FOUR, 1, 2"></div>
    <div class="formRow"><label for="cJours">Jour(s) (LMWJVSD)</label><input type="text" id="cJours" placeholder="Ex : LM, JVSD"></div>
    <div class="actionsGrid">
      <button id="saveClient" class="btnPrimary">Enregistrer</button>
      <button id="clearCreate" class="btnSecondary">Effacer</button>
    </div>
  </div>
</aside>

<!-- Panneau MODIFIER (droite) -->
<div id="editPanel">
  <div id="editHeader">
    <div id="editTitle">Modifier le client</div>
    <button id="closeEdit" title="Fermer">✕</button>
  </div>
  <div id="editBody">
    <input type="hidden" id="editId">
    <div class="formRow"><label for="eNom">Nom client</label><input type="text" id="eNom"></div>
    <div class="formRow"><label for="eCode">Code client</label><input type="number" id="eCode"></div>
    <div class="formRow"><label for="eAdresse">Adresse livraison</label><input type="text" id="eAdresse"></div>
    <div class="formRow"><label for="eLatitude">Latitude (optionnel)</label><input type="text" id="eLatitude" placeholder="Ex: 50.627"></div>
    <div class="formRow"><label for="eLongitude">Longitude (optionnel)</label><input type="text" id="eLongitude" placeholder="Ex: 3.058"></div>
    <div class="formRow"><label for="eTournee">Tournée</label><input type="text" id="eTournee" placeholder="Ex : T020, FOUR"></div>
    <div class="formRow"><label for="eJours">Jour(s) (LMWJVSD)</label><input type="text" id="eJours" placeholder="Ex : LM, JVSD"></div>
  </div>
  <div id="editActions">
    <button id="editSave" class="btnPrimary">Enregistrer</button>
    <button id="editCancel" class="btnSecondary">Annuler</button>
  </div>
</div>

<!-- Barre d’actions bas-gauche : Légende + Thème -->
<div id="legendActionBar">
  <button id="legendFab" class="actionBtn" title="Légende / filtres">☰</button>
  <button id="themeToggle" class="actionBtn" title="Basculer thème">☀️</button>
</div>
<div id="legendDrawer">
  <div id="legendHeader">
    <h4>Tournées visibles</h4>
    <span id="legendFilterBadge"></span>
    <span id="legendTotal"></span>
    <button id="legendExportBtn" title="Exporter CSV">Export</button>
    <button id="legendClearBtn" title="Réinitialiser">Reset</button>
  </div>
  <div id="tourLegendBody"></div>
</div>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
/* =================== State =================== */
let map=null, baseOSM=null, baseDark=null, currentBase='light';
let allClients=[], markers=[], marker_cluster=null;
let filterTourneesActive = new Set();   // légende : tournées activées (bleu)
let lastWorkingClients = [];
let isFirstLoad = true, shouldFitBounds = false;

/* Couleurs dynamiques par tournée */
const TOURNEE_COLORS = {}; let colorIndex=0;
function generateColor(i){ const hue = (i*47)%360; return `hsla(${hue},85%,45%,0.85)`; }
function getColorForTournee(t){ const k=(t||"AUTRE").toString().trim().toUpperCase(); if(!TOURNEE_COLORS[k]) TOURNEE_COLORS[k]=generateColor(colorIndex++); return TOURNEE_COLORS[k]; }

function getMap(){ for(const k in window){ if(k.startsWith('map_')) return window[k]; } return null; }
function escapeHtml(s){ return String(s||"").replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }

/* =================== API =================== */
async function fetchClients(params){
  const url = "http://127.0.0.1:5000/clients" + (params ? "?" + params.toString() : "");
  const r = await fetch(url); return await r.json();
}
async function createClient(payload){ return await fetch("http://127.0.0.1:5000/clients",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}); }
async function updateClient(id,payload){ return await fetch(`http://127.0.0.1:5000/clients/${id}`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}); }
async function removeClient(id){ return await fetch(`http://127.0.0.1:5000/clients/${id}`,{method:"DELETE"}); }

/* =================== Fonds de carte (OSM <-> Stadia Smooth Dark) =================== */
function initBaseLayers(){
  baseOSM = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{ attribution:'© OpenStreetMap', maxZoom:19});
  baseDark = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',{
    maxZoom: 20,
    attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://openstreetmap.org/">OpenStreetMap</a>'
  });
  baseOSM.addTo(map); currentBase='light';

  // Retire aussi le contrôle zoom natif (fallback)
  if(map.zoomControl && map.zoomControl.remove) map.zoomControl.remove();
}

/* Thème */
function setTheme(theme){
  if(theme==='dark'){
    document.body.classList.add('dark'); document.body.classList.remove('light');
    if(map.hasLayer(baseOSM)) map.removeLayer(baseOSM);
    if(!map.hasLayer(baseDark)) baseDark.addTo(map);
    document.getElementById('themeToggle').textContent = '🌙';
  }else{
    document.body.classList.remove('dark'); document.body.classList.add('light');
    if(map.hasLayer(baseDark)) map.removeLayer(baseDark);
    if(!map.hasLayer(baseOSM)) baseOSM.addTo(map);
    document.getElementById('themeToggle').textContent = '☀️';
  }
  currentBase = theme;
  try{ localStorage.setItem('map-theme', theme); }catch(e){}
}

/* =================== Chargement & filtres =================== */
async function loadClients(){
  try{
    const nom=document.getElementById("searchNom").value.trim();
    const code=document.getElementById("searchCode").value.trim();
    const jour=document.getElementById("searchJour").value.trim();
    const tournee=document.getElementById("searchTournee").value.trim();

    const params=new URLSearchParams();
    if(nom) params.append("nom",nom);
    if(code) params.append("code",code);
    if(jour){ params.append("jour",jour); params.append("jour_livraison",jour); }
    if(tournee){ params.append("tournee",tournee); params.append("num_tournee",tournee); }

    allClients = await fetchClients(params);
    displayMarkers();
    document.getElementById("resultCounter").innerText = `${allClients.length} client(s) trouvé(s)`;
  }catch(e){ console.error(e); }
}

/* =================== Markers / Cluster (typo homogène + iconCreateFunction) =================== */
function displayMarkers(){
  if(!marker_cluster){
    marker_cluster = L.markerClusterGroup({
      maxClusterRadius: 80,
      disableClusteringAtZoom: 14,
      iconCreateFunction: function(cluster){
        const count = cluster.getChildCount();
        // couleur moyenne basée sur 1er enfant
        const any = cluster.getAllChildMarkers()[0];
        const t = any && any.client ? (any.client.num_tournee||"AUTRE") : "AUTRE";
        const color = getColorForTournee(String(t).toUpperCase());
        const html = `<div style="
          background:${color};
          width:34px;height:34px;border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          box-shadow:0 3px 12px rgba(0,0,0,.35);">
          <span class="marker-cluster-count" style="font-weight:900;font-size:10px;color:#fff;text-transform:uppercase;">${count}</span>
        </div>`;
        return L.divIcon({ html, className:'', iconSize:[34,34] });
      }
    }).addTo(map);
  }else{
    marker_cluster.clearLayers();
  }
  markers=[];

  let working = allClients.filter(c=>{
    const lat=parseFloat(String(c.latitude||"").replace(",",".").replace(/[^0-9.\-]/g,""));
    const lon=parseFloat(String(c.longitude||"").replace(",",".").replace(/[^0-9.\-]/g,""));
    c.latitude=lat; c.longitude=lon;
    if(isNaN(lat)||isNaN(lon)) return false;
    if(lat<40||lat>52||lon<-5||lon>10) return false;
    return true;
  });

  // Filtrage Légende: si des tournées sont actives => ne montrer que celles-là
  if(filterTourneesActive.size>0){
    const keys=new Set(Array.from(filterTourneesActive).map(x=>x.toUpperCase()));
    working = working.filter(c=> keys.has((c.num_tournee||"AUTRE").toString().trim().toUpperCase()));
  }

  lastWorkingClients = working.slice();
  if(working.length===0){ updateTourLegend([]); return; }

  working.forEach(c=>{
    const t=(c.num_tournee??"").toString().trim();
    const color=getColorForTournee(t||"AUTRE");
    const label=(t||"").toUpperCase();
    const iconHTML = `<div class="client-marker" style="background:${color};">${escapeHtml(label)}</div>`;
    const icon=L.divIcon({html:iconHTML, className:"", iconSize:[28,28], iconAnchor:[14,14], popupAnchor:[0,-14]});
    const m=L.marker([c.latitude,c.longitude],{icon}).bindPopup(createPopupHTML(c), {autoPan:true, keepInView:true});
    m.client=c; marker_cluster.addLayer(m); markers.push(m);
  });

  if((isFirstLoad||shouldFitBounds)&&markers.length>0){
    const group=L.featureGroup(markers);
    map.fitBounds(group.getBounds(),{padding:[50,50]});
  }
  isFirstLoad=false; shouldFitBounds=false;

  updateTourLegend(working);
}

/* =================== Légende (fond bleu doux) =================== */
function updateTourLegend(clientsVisible){
  const body=document.getElementById("tourLegendBody");
  const badge=document.getElementById("legendFilterBadge");
  const legendTotal=document.getElementById("legendTotal");

  if(!clientsVisible || clientsVisible.length===0){
    body.innerHTML=""; if(legendTotal){ legendTotal.style.display="none"; legendTotal.textContent=""; }
    if(badge){ badge.style.display="none"; badge.textContent=""; }
    return;
  }

  const counts={};
  clientsVisible.forEach(c=>{ const k=(c.num_tournee||"AUTRE").toString().trim().toUpperCase()||"AUTRE"; counts[k]=(counts[k]||0)+1; });
  const items=Object.entries(counts).sort((a,b)=> b[1]-a[1] || a[0].localeCompare(b[0]));

  body.innerHTML = items.map(([label,n])=>{
    const color=getColorForTournee(label);
    const active=(filterTourneesActive.has(label))?"active":"";
    return `<div class="legendRow ${active}" data-tour="${label}">
      <span class="legendSw" style="background:${color};"></span>
      <span class="legendLabel" title="${label}">${label}</span>
      <span class="legendCount">${n}</span>
    </div>`;
  }).join("");

  legendTotal.style.display="inline-block";
  legendTotal.textContent=`Total visibles : ${clientsVisible.length}`;

  if(filterTourneesActive.size>0){
    const arr=Array.from(filterTourneesActive).sort();
    badge.style.display="inline-block"; badge.textContent=`Filtre : ${arr.join(", ")}`;
  }else{
    badge.style.display="none"; badge.textContent="";
  }

  Array.from(body.querySelectorAll(".legendRow")).forEach(row=>{
    row.addEventListener("click",()=>{
      const tour=row.getAttribute("data-tour"); if(!tour) return;
      if(filterTourneesActive.has(tour)) filterTourneesActive.delete(tour); else filterTourneesActive.add(tour);
      shouldFitBounds=true; displayMarkers();
    });
  });
}
function toggleLegend(){ document.getElementById("legendDrawer").classList.toggle("open"); }

/* =================== Export CSV visibles =================== */
function exportVisibleToCSV(){
  const rows=lastWorkingClients||[]; if(rows.length===0){ alert("Aucun client à exporter."); return; }
  const headers=["code_client","nom_client","adresse_livraison","latitude","longitude","num_tournee","jour_livraison"];
  const esc=v=>{ if(v==null) return ""; const s=String(v).replace(/"/g,'""'); return `"${s}"`; };
  const lines=[headers.join(",")];
  rows.forEach(c=>{
    lines.push([esc(c.code_client),esc(c.nom_client),esc(c.adresse_livraison),esc(c.latitude),esc(c.longitude),esc(c.num_tournee||""),esc(c.jour_livraison||"")].join(","));
  });
  const csv=lines.join("\n");
  const blob=new Blob([csv],{type:"text/csv;charset=utf-8;"}); const url=URL.createObjectURL(blob);
  const a=document.createElement("a"); a.href=url; a.download=`clients_visibles_${new Date().toISOString().replace(/[:.]/g,"-")}.csv`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
}

/* =================== Popup =================== */
function createPopupHTML(c){
  const nom=escapeHtml(c.nom_client||"Client inconnu");
  const adr=escapeHtml(c.adresse_livraison||"—");
  const code=escapeHtml(c.code_client||"—");
  const tour=escapeHtml(c.num_tournee||"—");
  const jours=escapeHtml(c.jour_livraison||"—");
  const lat=c.latitude, lon=c.longitude;
  const badgeColor=getColorForTournee(c.num_tournee||"AUTRE");
  const googleUrl = (lat!=null && lon!=null)
    ? `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`
    : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(c.adresse_livraison||"")}`;

  return `
  <div class="marker-popup advanced">
    <button class="popup-close" onclick="closePopup(this)" title="Fermer">✕</button>
    <div class="popup-header">
      <div class="popup-title">${nom}</div>
      <span class="tournee-badge" style="background:${badgeColor};">${tour}</span>
    </div>
    <div class="popup-info">
      <div class="field"><span class="field-label">📍 Adresse :</span> ${adr}</div>
      <div class="field"><span class="field-label">🏷️ Code client :</span> ${code}</div>
      <div class="field"><span class="field-label">🚚 Tournée :</span> ${tour}</div>
      <div class="field"><span class="field-label">📅 Jours :</span> ${jours}</div>
    </div>
    <hr>
    <div class="popup-actions">
      <button class="btn btn-primary" onclick="openEditPanel(${c.id})">✏️ Modifier</button>
      <button class="btn btn-danger" onclick="deleteClient(${c.id})">🗑️ Supprimer</button>
      ${ (lat!=null && lon!=null) ? `<button class="btn btn-secondary" onclick="centerOnClient(${lat},${lon})">📍 Centrer</button>` : "" }
      <a class="btn btn-map" href="${googleUrl}" target="_blank">🗺️ Itinéraire</a>
    </div>
  </div>`;
}
function closePopup(btn){ const mp=getMap(); if(mp&&mp.closePopup) mp.closePopup(); }
function centerOnClient(lat,lon){ if(!map) return; map.setView([lat,lon], 15, {animate:true}); }

/* =================== CRUD côté UI =================== */
function clearCreateForm(){ ["cNom","cCode","cAdresse","cLatitude","cLongitude","cTournee","cJours"].forEach(id=>document.getElementById(id).value=""); }
async function saveClient(){
  const payload={
    nom_client: document.getElementById("cNom").value.trim(),
    code_client: parseInt(document.getElementById("cCode").value)||null,
    adresse_livraison: document.getElementById("cAdresse").value.trim(),
    latitude: document.getElementById("cLatitude").value.trim(),
    longitude: document.getElementById("cLongitude").value.trim(),
    num_tournee: document.getElementById("cTournee").value.trim(),
    jour_livraison: document.getElementById("cJours").value.trim()
  };
  if(!payload.nom_client){ alert("Nom client obligatoire."); return; }
  if(!payload.code_client){ alert("Code client obligatoire."); return; }
  if(!payload.adresse_livraison){ alert("Adresse livraison obligatoire."); return; }

  const resp=await createClient(payload);
  const out=await resp.json().catch(()=>({}));
  if(!resp.ok){ alert(out.error || "Erreur lors de la création."); return; }
  clearCreateForm(); loadClients();
}
async function deleteClient(id){ if(!confirm("Supprimer ce client ?")) return; await removeClient(id); await loadClients(); }

/* Edit Panel */
function openEditPanel(id){
  const c=allClients.find(x=>x.id===id); if(!c) return;
  document.getElementById("editId").value = c.id;
  document.getElementById("eNom").value = c.nom_client||"";
  document.getElementById("eCode").value = c.code_client||"";
  document.getElementById("eAdresse").value = c.adresse_livraison||"";
  document.getElementById("eLatitude").value = (c.latitude ?? "");
  document.getElementById("eLongitude").value = (c.longitude ?? "");
  document.getElementById("eTournee").value = c.num_tournee||"";
  document.getElementById("eJours").value = c.jour_livraison||"";
  document.getElementById("editPanel").classList.add("open");
}
function closeEditPanel(){ document.getElementById("editPanel").classList.remove("open"); }
async function saveEdit(){
  const id = parseInt(document.getElementById("editId").value);
  const payload={
    nom_client: document.getElementById("eNom").value.trim(),
    code_client: parseInt(document.getElementById("eCode").value)||null,
    adresse_livraison: document.getElementById("eAdresse").value.trim(),
    latitude: document.getElementById("eLatitude").value.trim(),
    longitude: document.getElementById("eLongitude").value.trim(),
    num_tournee: document.getElementById("eTournee").value.trim(),
    jour_livraison: document.getElementById("eJours").value.trim()
  };
  if(!payload.nom_client){ alert("Nom obligatoire."); return; }
  if(!payload.code_client){ alert("Code client obligatoire."); return; }
  if(!payload.adresse_livraison){ alert("Adresse obligatoire."); return; }

  const resp=await updateClient(id,payload);
  const out=await resp.json().catch(()=>({}));
  if(!resp.ok){ alert(out.error || "Erreur lors de la mise à jour."); return; }
  await loadClients(); closeEditPanel();
}

/* =================== Init =================== */
document.addEventListener("DOMContentLoaded", ()=>{
  map = (function(){ for(const k in window){ if(k.startsWith('map_')) return window[k]; } })();

  // Fonds + thème initial
  initBaseLayers();
  const storedTheme = (localStorage.getItem('map-theme')||'light');
  setTheme(storedTheme);

  // Cluster créé dans displayMarkers()
  loadClients();

  // Menu latéral (gauche)
  document.getElementById("leftMenuToggle").onclick = ()=> document.getElementById("leftMenu").classList.add("open");
  document.getElementById("leftMenuClose").onclick  = ()=> document.getElementById("leftMenu").classList.remove("open");

  // Actions recherche/création
  document.getElementById("searchBtnApply").onclick = ()=>{ loadClients(); };
  document.getElementById("resetBtn").onclick = ()=>{
    ["searchNom","searchCode","searchJour","searchTournee"].forEach(id=>document.getElementById(id).value="");
    loadClients();
  };
  document.getElementById("saveClient").onclick = saveClient;
  document.getElementById("clearCreate").onclick = clearCreateForm;

  // Panneau Edit
  document.getElementById("editSave").onclick = saveEdit;
  document.getElementById("editCancel").onclick = closeEditPanel;
  document.getElementById("closeEdit").onclick = closeEditPanel;

  // Légende + Thème (bas-gauche)
  document.getElementById("legendFab").onclick = toggleLegend;
  document.getElementById("legendClearBtn").onclick = ()=>{ filterTourneesActive.clear(); shouldFitBounds=true; displayMarkers(); };
  document.getElementById("legendExportBtn").onclick = exportVisibleToCSV;
  document.getElementById("themeToggle").onclick = ()=> setTheme(currentBase==='light'?'dark':'light');

  // Update dynamique recherche (au fil de la saisie)
  ["searchNom","searchCode","searchJour","searchTournee"].forEach(id=>{
    document.getElementById(id).addEventListener("input", ()=>{ loadClients(); });
  });
});
</script>
"""

m.get_root().html.add_child(folium.Element(html))
m.save("index.html")
print("✅ UI mise à jour -> index.html (légende fond bleu doux, toggle thème à côté du hamburger, menu latéral ouvrable à gauche, popup badge sans croix, clusters/markers typographiés, zoom +/- supprimés, panneau modification harmonisé)")
