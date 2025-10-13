from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

# Connexion PostgreSQL
conn = psycopg2.connect(
    dbname="maps_test",
    user="postgres",
    password="Foot2562_",
    host="localhost",
    port="5432"
)

color_map = {
    1: "rgba(0,123,255,0.6)",   # bleu
    2: "rgba(40,167,69,0.6)",   # vert
    3: "rgba(255,193,7,0.6)",   # jaune
    4: "rgba(253,126,20,0.6)",  # orange
    5: "rgba(220,53,69,0.6)",   # rouge
}

@app.route("/clients", methods=["GET"])
def get_clients():
    jour = request.args.get("jour")
    try:
        cur = conn.cursor()
        if jour:
            cur.execute("""
                SELECT id, "Code client", "Nom client", "adresse livraison",
                       "Latitude", "Longitude", couleur, tournee, jours_livraison
                FROM client
                WHERE jours_livraison ILIKE %s
            """, (f"%{jour}%",))
        else:
            cur.execute("""
                SELECT id, "Code client", "Nom client", "adresse livraison",
                       "Latitude", "Longitude", couleur, tournee, jours_livraison
                FROM client
            """)
        rows = cur.fetchall()
        cur.close()

        clients = []
        for r in rows:
            try: lat = float(str(r[4]).replace(',', '.')) if r[4] else None
            except: lat = None
            try: lon = float(str(r[5]).replace(',', '.')) if r[5] else None
            except: lon = None
            clients.append({
                "id": r[0],
                "code_client": r[1],
                "nom_client": r[2],
                "adresse_complete": r[3],
                "latitude": lat,
                "longitude": lon,
                "couleur": r[6] if r[6] else "rgba(111,66,193,0.6)",
                "tournee": r[7] if r[7] else 0,
                "jours_livraison": r[8] if r[8] else ""
            })
        return jsonify(clients)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clients", methods=["POST"])
def add_client():
    try:
        data = request.json
        tournee = int(data.get("tournee") or 0)
        couleur = color_map.get(tournee, "rgba(111,66,193,0.6)")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO client ("Code client", "Nom client", "adresse livraison",
                                "Latitude", "Longitude", couleur, tournee, jours_livraison)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            data.get("code_client"),
            data.get("nom_client"),
            data.get("adresse_complete"),
            str(data.get("latitude") or ''),
            str(data.get("longitude") or ''),
            couleur,
            tournee,
            data.get("jours_livraison") or ""
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clients/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    try:
        data = request.json
        tournee = int(data.get("tournee") or 0)
        couleur = color_map.get(tournee, "rgba(111,66,193,0.6)")
        cur = conn.cursor()
        cur.execute("""
            UPDATE client
            SET "Code client"=%s, "Nom client"=%s, "adresse livraison"=%s,
                "Latitude"=%s, "Longitude"=%s, couleur=%s, tournee=%s, jours_livraison=%s
            WHERE id=%s
        """, (
            data.get("code_client"),
            data.get("nom_client"),
            data.get("adresse_complete"),
            str(data.get("latitude") or ''),
            str(data.get("longitude") or ''),
            couleur,
            tournee,
            data.get("jours_livraison") or "",
            client_id
        ))
        conn.commit()
        cur.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM client WHERE id=%s", (client_id,))
        conn.commit()
        cur.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
