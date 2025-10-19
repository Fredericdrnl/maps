import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

# ------------------------------
# Config connexion PostgreSQL
# ------------------------------
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGDATABASE = os.getenv("PGDATABASE", "maps")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "Foot2562_")

# ------------------------------
# Config Nominatim (géocodage)
# ------------------------------
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "client-map-app/1.0 (contact@example.com)"
}
NOMINATIM_DEFAULT_PARAMS = {
    "format": "json",
    "addressdetails": 1,
    "countrycodes": "fr",
    "accept-language": "fr",
    "viewbox": "-1.5,51.5,5.0,48.5",
    "bounded": 1,
    "limit": 1
}

app = Flask(__name__)
CORS(app)

# ------------------------------
# Connexion DB
# ------------------------------
def get_conn():
    return psycopg2.connect(
        host=PGHOST, port=PGPORT, dbname=PGDATABASE,
        user=PGUSER, password=PGPASSWORD
    )

def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            code_client INTEGER,
            nom_client TEXT,
            adresse_livraison TEXT,
            latitude TEXT,
            longitude TEXT,
            couleur VARCHAR(20),
            tournee VARCHAR(10),
            jours_livraison VARCHAR(10)
        );
        """)
        conn.commit()

# ------------------------------
# Géocodage adresse
# ------------------------------
def geocode_address(address: str):
    if not address:
        return None
    params = dict(NOMINATIM_DEFAULT_PARAMS)
    params["q"] = address
    try:
        r = requests.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data:
            return None
        return str(data[0]["lat"]), str(data[0]["lon"])
    except Exception:
        return None

# ------------------------------
# Utils
# ------------------------------
def row_to_client(row: dict):
    return {
        "id": row["id"],
        "code_client": row["code_client"],
        "nom_client": row["nom_client"],
        "adresse_livraison": row["adresse_livraison"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "couleur": row["couleur"],
        "tournee": row["tournee"],
        "jours_livraison": row["jours_livraison"]
    }

# ------------------------------
# Routes API
# ------------------------------

# 📍 GET - Liste + filtres
@app.route("/clients", methods=["GET"])
def list_clients():
    nom = request.args.get("nom", "").strip()
    code = request.args.get("code", "").strip()
    jour = request.args.get("jour", "").strip()
    tournee = request.args.get("tournee", "").strip()

    where = []
    params = {}
    if nom:
        where.append("nom_client ILIKE %(nom)s")
        params["nom"] = f"%{nom}%"
    if code:
        where.append("CAST(code_client AS TEXT) ILIKE %(code)s")
        params["code"] = f"%{code}%"
    if jour:
        where.append("jours_livraison ILIKE %(jour)s")
        params["jour"] = f"%{jour}%"
    if tournee:
        where.append("tournee ILIKE %(tournee)s")
        params["tournee"] = f"%{tournee}%"

    sql = "SELECT * FROM clients"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"

    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        return jsonify([row_to_client(r) for r in rows])

# 📍 POST - Créer un client
@app.route("/clients", methods=["POST"])
def create_client():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "JSON invalide"}), 400

    nom = (payload.get("nom_client") or "").strip()
    code_client = payload.get("code_client")
    adresse = (payload.get("adresse_livraison") or "").strip()
    lat = (payload.get("latitude") or "").strip()
    lon = (payload.get("longitude") or "").strip()
    tournee = (payload.get("tournee") or "").strip()
    jours = (payload.get("jours_livraison") or "").strip()
    couleur = (payload.get("couleur") or "").strip() or None

    if not nom:
        return jsonify({"error": "nom_client est obligatoire"}), 400
    if not code_client:
        return jsonify({"error": "code_client est obligatoire"}), 400
    if not adresse:
        return jsonify({"error": "adresse_livraison est obligatoire"}), 400

    if not lat or not lon:
        geo = geocode_address(adresse)
        if not geo:
            return jsonify({"error": "Adresse introuvable (géocodage)."}), 400
        lat, lon = geo

    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO clients (code_client, nom_client, adresse_livraison, latitude, longitude, couleur, tournee, jours_livraison)
            VALUES (%(code_client)s, %(nom)s, %(adresse)s, %(lat)s, %(lon)s, %(couleur)s, %(tournee)s, %(jours)s)
            RETURNING *;
        """, {
            "code_client": code_client,
            "nom": nom,
            "adresse": adresse,
            "lat": lat,
            "lon": lon,
            "couleur": couleur,
            "tournee": tournee,
            "jours": jours
        })
        row = cur.fetchone()
        conn.commit()
        return jsonify(row_to_client(row)), 201

# 📍 PUT - Modifier un client
@app.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id: int):
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "JSON invalide"}), 400

    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM clients WHERE id=%s", (client_id,))
        current = cur.fetchone()
        if not current:
            return jsonify({"error": "Client introuvable"}), 404

        nom = (payload.get("nom_client") or current["nom_client"] or "").strip()
        code_client = payload.get("code_client", current["code_client"])
        adresse = (payload.get("adresse_livraison") or current["adresse_livraison"] or "").strip()
        lat = (payload.get("latitude") or "").strip()
        lon = (payload.get("longitude") or "").strip()
        tournee = (payload.get("tournee") or current["tournee"] or "").strip()
        jours = (payload.get("jours_livraison") or current["jours_livraison"] or "").strip()
        couleur = (payload.get("couleur") or current["couleur"])

        if not nom:
            return jsonify({"error": "nom_client est obligatoire"}), 400
        if not code_client:
            return jsonify({"error": "code_client est obligatoire"}), 400
        if not adresse:
            return jsonify({"error": "adresse_livraison est obligatoire"}), 400

        address_changed = (adresse != (current["adresse_livraison"] or ""))

        if not lat or not lon:
            if address_changed:
                geo = geocode_address(adresse)
                if not geo:
                    return jsonify({"error": "Adresse introuvable (géocodage)."}), 400
                lat, lon = geo
            else:
                lat = current["latitude"]
                lon = current["longitude"]
                if (not lat) or (not lon):
                    geo = geocode_address(adresse)
                    if not geo:
                        return jsonify({"error": "Adresse introuvable (géocodage)."}), 400
                    lat, lon = geo

        cur.execute("""
            UPDATE clients
            SET code_client=%(code)s,
                nom_client=%(nom)s,
                adresse_livraison=%(adresse)s,
                latitude=%(lat)s,
                longitude=%(lon)s,
                couleur=%(couleur)s,
                tournee=%(tournee)s,
                jours_livraison=%(jours)s
            WHERE id=%(id)s
            RETURNING *;
        """, {
            "code": code_client,
            "nom": nom,
            "adresse": adresse,
            "lat": lat,
            "lon": lon,
            "couleur": couleur,
            "tournee": tournee,
            "jours": jours,
            "id": client_id
        })
        row = cur.fetchone()
        conn.commit()
        return jsonify(row_to_client(row)), 200

# 📍 DELETE - Supprimer un client
@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE id=%s RETURNING id;", (client_id,))
        deleted = cur.fetchone()
        conn.commit()
        if not deleted:
            return jsonify({"error": "Client introuvable"}), 404
        return jsonify({"status": "ok", "deleted_id": client_id}), 200

# ------------------------------
# Entrée
# ------------------------------
if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
