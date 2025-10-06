import pandas as pd

# --- Étape 1 : Charger le fichier Excel ---
file_path = "FICHIER_CLIENTS.xlsx"  # Mets ici le nom exact de ton fichier
excel_file = pd.ExcelFile(file_path)

# --- Étape 2 : Charger la feuille principale ---
df = pd.read_excel(excel_file, sheet_name='Sheet1')

# --- Étape 3 : Nettoyer les en-têtes et supprimer la première ligne redondante ---
df.columns = df.iloc[0]
df = df.drop(index=0).reset_index(drop=True)

# --- Étape 4 : Fusionner les deux colonnes d’adresse de livraison ---
df["Adresse livraison complète"] = (
    df["Adresse liv adr1"].fillna('') + ' ' + df["Adresse liv adr2"].fillna('')
).str.strip()

# --- Étape 5 : Supprimer les anciennes colonnes ---
df = df.drop(columns=["Adresse liv adr1", "Adresse liv adr2"])

# --- Étape 6 : Sauvegarder le fichier final ---
output_path = "FICHIER_CLIENTS_ADRESSE_FUSIONNEE.xlsx"
df.to_excel(output_path, index=False)

print(f"✅ Fichier exporté : {output_path}")
