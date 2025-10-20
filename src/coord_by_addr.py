import pandas as pd

# 📁 Fichiers d'entrée et de sortie
base_file = "FICHIER CLIENTS GLOBAL(2).xlsx"  # Fichier de base
geo_file = "8669bc87-27f6-41b9-840b-36bfde927957.xlsx"  # Fichier avec coordonnées
output_file = "clients_fusion_geocode.xlsx"  # Fichier final fusionné
missing_file = "clients_sans_coordonnees.xlsx"  # Liste des clients sans coordonnées

# 📊 Charger les fichiers Excel
df_base = pd.read_excel(base_file)
df_geo = pd.read_excel(geo_file)

# ✅ S'assurer que la colonne "Code client" est bien une chaîne pour éviter les erreurs de correspondance
df_base["Code client"] = df_base["Code client"].astype(str).str.strip()
df_geo["Code client"] = df_geo["Code client"].astype(str).str.strip()

# 📍 Sélectionner uniquement les colonnes utiles dans le fichier coordonnées
df_geo_coords = df_geo[["Code client", "Latitude", "Longitude"]]

# 🔄 Fusionner les coordonnées sur le fichier de base
df_merged = pd.merge(
    df_base,
    df_geo_coords,
    on="Code client",
    how="left",
    suffixes=("", "_from_geo")
)

# 🛠️ Créer ou remplacer les colonnes Latitude/Longitude
df_merged["Latitude"] = df_merged["Latitude_from_geo"]
df_merged["Longitude"] = df_merged["Longitude_from_geo"]

# 🧹 Supprimer les colonnes temporaires
df_merged.drop(columns=[col for col in df_merged.columns if col.endswith("_from_geo")], inplace=True)

# 💾 Sauvegarder le fichier fusionné complet
df_merged.to_excel(output_file, index=False)
print(f"✅ Fichier fusionné enregistré : {output_file}")

# 📍 Extraire les clients sans coordonnées
df_missing = df_merged[df_merged["Latitude"].isna() | df_merged["Longitude"].isna()]

if not df_missing.empty:
    df_missing.to_excel(missing_file, index=False)
    print(f"⚠️ {len(df_missing)} clients sans coordonnées. Liste enregistrée : {missing_file}")
else:
    print("🎉 Toutes les lignes ont des coordonnées !")

# 📊 Afficher un aperçu des 10 premières lignes
print("\n📌 Aperçu du résultat fusionné :")
print(df_merged.head(10))
