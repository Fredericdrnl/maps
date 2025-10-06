from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Foot2562_@localhost:5432/maps'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/clients/*": {"origins": "*"}})
db = SQLAlchemy(app)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    code_client = db.Column(db.String(50))
    nom_client = db.Column(db.String(100))
    jours_livraison = db.Column(db.String(10))
    adresse_complete = db.Column(db.Text)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    couleur = db.Column(db.String(20))
    tournee = db.Column(db.Integer)

@app.route("/clients", methods=["GET"])
@cross_origin()
def get_clients():
    jours = request.args.get("jours")  # ex: L,M,W
    nom = request.args.get("nom")      # recherche partielle
    query = Client.query
    if jours:
        jours_list = jours.split(",")
        conditions = [Client.jours_livraison.ilike(f"%{j}%") for j in jours_list]
        query = query.filter(or_(*conditions))
    if nom:
        query = query.filter(Client.nom_client.ilike(f"%{nom}%"))
    clients = query.all()
    return jsonify([{
        "id": c.id,
        "code_client": c.code_client,
        "nom_client": c.nom_client,
        "jours_livraison": c.jours_livraison,
        "adresse_complete": c.adresse_complete,
        "longitude": c.longitude,
        "latitude": c.latitude,
        "couleur": c.couleur,
        "tournee": c.tournee
    } for c in clients])

@app.route("/clients", methods=["POST"])
@cross_origin()
def add_client():
    data = request.json
    client = Client(
        code_client=data.get("code_client"),
        nom_client=data.get("nom_client"),
        jours_livraison=data.get("jours_livraison"),
        adresse_complete=data.get("adresse_complete"),
        longitude=data.get("longitude"),
        latitude=data.get("latitude"),
        couleur=data.get("couleur","blue"),
        tournee=data.get("tournee",0)
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({"success": True, "id": client.id})

@app.route("/clients/<int:client_id>", methods=["DELETE"])
@cross_origin()
def delete_client(client_id):
    client = Client.query.get(client_id)
    if client:
        db.session.delete(client)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error":"Client non trouvé"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
