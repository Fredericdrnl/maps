import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

# === 1. Charger le fichier Excel ===
fichier_entree = "adresses.xlsx"  # <-- Mets le nom exact de ton fichier
fichier_sortie = "adresses_geocodees.xlsx"

# Lire le fichier Excel (première feuille par défaut)
df = pd.read_excel(fichier_entree)

# === 2. Identifier la colonne C ===
# Si la colonne C contient les adresses, on la récupère :
colonne_adresse = df.columns[2]  # colonne C = index 2 (A=0, B=1, C=2)

# === 3. Créer les colonnes Latitude / Longitude ===
df["Latitude"] = None
df["Longitude"] = None

# === 4. Initialiser le géocodeur ===
geolocator = Nominatim(user_agent="geoapi_exercice")

# === 5. Géocoder chaque adresse ===
for i, adresse in enumerate(df[colonne_adresse]):
    if pd.isna(adresse):
        continue  # ignorer les lignes vides
    try:
        location = geolocator.geocode(adresse)
        if location:
            df.at[i, "Latitude"] = location.latitude
            df.at[i, "Longitude"] = location.longitude
            print(f"{i+1}/{len(df)} ✓ {adresse} -> ({location.latitude}, {location.longitude})")
        else:
            print(f"{i+1}/{len(df)} ✗ Adresse introuvable : {adresse}")
    except Exception as e:
        print(f"{i+1}/{len(df)} ⚠️ Erreur pour {adresse} : {e}")
    sleep(1)  # éviter de surcharger le serveur (Nominatim limite les requêtes)

# === 6. Enregistrer le résultat ===
df.to_excel(fichier_sortie, index=False)
print(f"\n✅ Fini ! Résultats enregistrés dans : {fichier_sortie}")
