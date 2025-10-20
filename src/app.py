# -*- coding: utf-8 -*-
import os
import re
import json
import requests
from typing import Optional, Tuple, Dict, Any, List

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras

# =========================
# Configuration PostgreSQL
# =========================
DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "maps"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "Foot2562_"),
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "clients-mapping-app/1.0 (contact: you@example.com)"
}

app = Flask(__name__)
CORS(app)


# =========================
# Utilitaires
# =========================
def get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('UTF8')  # ✅ force UTF-8 côté client PostgreSQL
    conn.autocommit = True
    return conn


def ensure_table():
    ddl = """
    CREATE TABLE IF NOT EXISTS clients (
        id SERIAL PRIMARY KEY,
        "code_client" INTEGER,
        "nom_client" TEXT,
        "adresse_livraison" TEXT,
        "latitude" TEXT,
        "longitude" TEXT,
        "num_tournee" TEXT,
        "jour_livraison" TEXT
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)


def to_float_or_none(val: Optional[str]) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip()
    if s == "":
        return None
    s = re.sub(r"[^0-9\-,\.]", "", s).replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    if not address or not address.strip():
        return None
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "fr",
        "accept-language": "fr",
    }
    try:
        r = requests.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        lat = to_float_or_none(data[0].get("lat"))
        lon = to_float_or_none(data[0].get("lon"))
        if lat is None or lon is None:
            return None
        return (lat, lon)
    except Exception:
        return None


def row_to_client(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "code_client": row["code_client"],
        "nom_client": row["nom_client"],
        "adresse_livraison": row["adresse_livraison"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "num_tournee": row["num_tournee"],
        "jour_livraison": row["jour_livraison"],
    }


def normalize_days(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    return s.strip().upper() or None


# =========================
# Gestion des erreurs JSON
# =========================
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Bad Request", detail=str(e)), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not Found", detail=str(e)), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="Internal Server Error", detail=str(e)), 500


def json_error(msg: str, code: int = 400):
    return jsonify({"error": msg}), code


# =========================
# Routes principales
# =========================
@app.route("/clients", methods=["GET"])
def list_clients():
    args = request.args
    nom = args.get("nom")
    code = args.get("code")
    raw_tournee = args.get("num_tournee") or args.get("tournee")
    raw_jour = args.get("jour_livraison") or args.get("jour")

    where = []
    params: List[Any] = []

    if nom:
        where.append('"nom_client" ILIKE %s')
        params.append(f"%{nom}%")

    if code:
        try:
            code_int = int(code)
            where.append('"code_client" = %s')
            params.append(code_int)
        except ValueError:
            where.append('CAST("code_client" AS TEXT) ILIKE %s')
            params.append(f"%{code}%")

    if raw_tournee:
        where.append('"num_tournee" ILIKE %s')
        params.append(f"%{raw_tournee}%")

    if raw_jour:
        where.append('"jour_livraison" ILIKE %s')
        params.append(f"%{raw_jour}%")

    sql = """
        SELECT id, "code_client", "nom_client", "adresse_livraison",
               "latitude", "longitude", "num_tournee", "jour_livraison"
        FROM clients
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        return jsonify([row_to_client(r) for r in rows])


@app.route("/clients", methods=["POST"])
def create_client():
    try:
        data = request.get_json(force=True, silent=False) or {}
    except Exception:
        return json_error("Corps JSON invalide", 400)

    nom_client = data.get("nom_client")
    code_client = data.get("code_client")
    adresse = data.get("adresse_livraison")

    if not nom_client:
        return json_error("nom_client est obligatoire", 400)
    if code_client in (None, ""):
        return json_error("code_client est obligatoire", 400)
    if not adresse:
        return json_error("adresse_livraison est obligatoire", 400)

    jour_livraison = normalize_days(data.get("jour_livraison"))
    num_tournee = (data.get("num_tournee") or "").strip() or None

    lat_str = data.get("latitude")
    lon_str = data.get("longitude")

    lat = to_float_or_none(lat_str)
    lon = to_float_or_none(lon_str)

    if lat is None or lon is None:
        coords = geocode_address(adresse)
        if not coords:
            return json_error("Adresse introuvable - géocodage impossible", 400)
        lat_out = f"{coords[0]}"
        lon_out = f"{coords[1]}"
    else:
        lat_out = f"{lat}"
        lon_out = f"{lon}"

    sql = """
        INSERT INTO clients ("code_client", "nom_client", "adresse_livraison", "latitude", "longitude", "num_tournee", "jour_livraison")
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        RETURNING id, "code_client", "nom_client", "adresse_livraison", "latitude", "longitude", "num_tournee", "jour_livraison";
    """
    vals = (code_client, nom_client, adresse, lat_out, lon_out, num_tournee, jour_livraison)

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, vals)
        row = cur.fetchone()
        return jsonify(row_to_client(row)), 201


@app.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id: int):
    try:
        data = request.get_json(force=True, silent=False) or {}
    except Exception:
        return json_error("Corps JSON invalide", 400)

    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute('SELECT * FROM clients WHERE id=%s', (client_id,))
        current = cur.fetchone()
        if not current:
            return json_error("Client introuvable", 404)

        code_client = data.get("code_client", current["code_client"])
        nom_client = data.get("nom_client", current["nom_client"])
        adresse_livraison = data.get("adresse_livraison", current["adresse_livraison"])
        num_tournee = (data.get("num_tournee")
                       if data.get("num_tournee") is not None
                       else current["num_tournee"])
        jour_livraison = normalize_days(
            data.get("jour_livraison", current["jour_livraison"])
        )

        lat_str = data.get("latitude", current["latitude"])
        lon_str = data.get("longitude", current["longitude"])

        if "latitude" in data or "longitude" in data:
            lat = to_float_or_none(lat_str)
            lon = to_float_or_none(lon_str)
            if lat is not None and lon is not None:
                latitude_out = f"{lat}"
                longitude_out = f"{lon}"
            else:
                coords = geocode_address(adresse_livraison)
                if not coords:
                    return json_error("Adresse introuvable - géocodage impossible", 400)
                latitude_out = f"{coords[0]}"
                longitude_out = f"{coords[1]}"
        else:
            if (adresse_livraison or "") != (current["adresse_livraison"] or ""):
                coords = geocode_address(adresse_livraison)
                if not coords:
                    return json_error("Adresse introuvable - géocodage impossible", 400)
                latitude_out = f"{coords[0]}"
                longitude_out = f"{coords[1]}"
            else:
                latitude_out = current["latitude"]
                longitude_out = current["longitude"]

        sql = """
            UPDATE clients
            SET "code_client"=%s, "nom_client"=%s, "adresse_livraison"=%s,
                "latitude"=%s, "longitude"=%s,
                "num_tournee"=%s, "jour_livraison"=%s
            WHERE id=%s
            RETURNING id, "code_client", "nom_client", "adresse_livraison", "latitude", "longitude", "num_tournee", "jour_livraison";
        """
        vals = (
            code_client, nom_client, adresse_livraison,
            latitude_out, longitude_out, num_tournee, jour_livraison, client_id
        )
        cur.execute(sql, vals)
        row = cur.fetchone()
        return jsonify(row_to_client(row))


@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('DELETE FROM clients WHERE id=%s', (client_id,))
        if cur.rowcount == 0:
            return json_error("Client introuvable", 404)
    return jsonify({"status": "ok", "deleted_id": client_id})


# =========================
# Entrée principale
# =========================
if __name__ == "__main__":
    ensure_table()
    port = int(os.getenv("PORT", "5000"))
    debug = bool(int(os.getenv("FLASK_DEBUG", "1")))
    app.run(host="0.0.0.0", port=port, debug=debug)
