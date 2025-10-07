from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from geopy.geocoders import Nominatim

app = Flask(__name__)
CORS(app)

# Connexion PostgreSQL
conn = psycopg2.connect(
    dbname="maps",
    user="postgres",
    password="Foot2562_",
    host="localhost",
    port="5432"
)

geolocator = Nominatim(user_agent="my_app")

def geocode_address(address):
    """Retourne (latitude, longitude) ou (None, None) si échec"""
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

@app.route("/clients", methods=["GET"])
def get_clients():
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients")
    rows = cur.fetchall()
    columns = ["id","code_client","nom_client","jours_livraison","adresse_complete",
               "longitude","latitude","couleur","tournee"]
    
    clients = []
    for r in rows:
        client = dict(zip(columns, r))
        # Si pas de coords mais adresse présente, géocoder
        if (not client["latitude"] or not client["longitude"]) and client["adresse_complete"]:
            lat, lon = geocode_address(client["adresse_complete"])
            if lat and lon:
                client["latitude"] = lat
                client["longitude"] = lon
                cur_update = conn.cursor()
                cur_update.execute(
                    "UPDATE clients SET latitude=%s, longitude=%s WHERE id=%s",
                    (lat, lon, client["id"])
                )
                conn.commit()
                cur_update.close()
        clients.append(client)
    
    cur.close()
    return jsonify(clients)

@app.route("/clients", methods=["POST"])
def add_client():
    data = request.json
    lat = data.get("latitude")
    lon = data.get("longitude")
    
    # Géocode si pas de coords
    if (lat is None or lon is None) and data.get("adresse_complete"):
        lat, lon = geocode_address(data["adresse_complete"])
        if lat is None or lon is None:
            return jsonify({"error":"Adresse introuvable"}), 400
    
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clients (code_client, nom_client, jours_livraison, adresse_complete, longitude, latitude, couleur, tournee)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["code_client"], data["nom_client"], data["jours_livraison"], 
        data["adresse_complete"], lon, lat, data.get("couleur","blue"), data.get("tournee",0)
    ))
    conn.commit()
    cur.close()
    return jsonify({"status":"ok"})

@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id=%s", (client_id,))
    conn.commit()
    cur.close()
    return jsonify({"status":"deleted"})

if __name__ == "__main__":
    app.run(debug=True)
