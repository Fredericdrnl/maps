import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

# 1️⃣ Charger ton fichier Excel
fichier_excel = "clients.xlsx"  # Remplace par le nom exact de ton fichier
df = pd.read_excel(fichier_excel)

# 2️⃣ Créer une colonne "Adresse complète" si elle n'existe pas
#    On concatène CP, ville et rue
df['Adresse complète'] = df['Adresse liv cp'].astype(str) + ", " + \
                        df['Adresse liv ville'].astype(str) + ", " + \
                        df['Adresse livraison rue'].astype(str)

# 3️⃣ Initialiser le géocodeur
geolocator = Nominatim(user_agent="geo_calculator")

# 4️⃣ Fonction pour récupérer latitude et longitude
def get_lat_lon(adresse):
    try:
        location = geolocator.geocode(adresse)
        sleep(1)  # Respect de la limite de Nominatim : 1 requête/seconde
        if location:
            return pd.Series([location.latitude, location.longitude])
        else:
            return pd.Series([None, None])
    except:
        return pd.Series([None, None])

# 5️⃣ Appliquer la fonction sur la colonne 'Adresse complète'
df[['Latitude', 'Longitude']] = df['Adresse complète'].apply(get_lat_lon)

# 6️⃣ Sauvegarder le fichier final
df.to_excel("fichier_avec_coordonnees.xlsx", index=False)

print("✅ Géocodage terminé et colonnes Latitude/Longitude ajoutées.")
