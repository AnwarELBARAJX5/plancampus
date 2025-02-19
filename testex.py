import pandas as pd
import os
import geojson
import Batiment
import DatabaseManager
from DatabaseManager import *
import osmnx as ox

# Chemin des fichiers GeoJSON
path = r"C:\Users\anwar\Desktop\projetinfo\batgeojson"
file = geojson.get_geojson_files(path)  # Liste des fichiers .geojson
liste_path = geojson.path(path)  # Liste des chemins complets des fichiers

# Afficher les fichiers et chemins
print(file)
print(liste_path)

# Création des DataFrames avec les bonnes colonnes
df = pd.DataFrame(file, columns=["Nom_batiment"])
df_nouvelles = pd.DataFrame(liste_path, columns=["path"])

# Fusionner les DataFrames
df = pd.concat([df, df_nouvelles], axis=1, ignore_index=False)




print(df)

# Sauvegarder en fichier Excel
df.to_excel("fichiers_geojso.xlsx", index=False)


import osmnx as ox
import geopandas as gpd

# Définir le lieu exact
lieu = "Aix-Marseille Université - campus de saint charles"

# Récupérer la zone sous forme de polygone
zone_universite = ox.geocode_to_gdf(lieu)

# Télécharger uniquement les routes dans cette zone
G = ox.graph_from_polygon(zone_universite.unary_union, network_type="walk", simplify=True)

# Convertir en GeoDataFrame
gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

# Sauvegarder en GeoJSON
gdf_edges.to_file("routes_universite.geojson", driver="GeoJSON")

print("Export terminé : fichier routes_universite.geojson")



# Télécharger les bâtiments avec leurs informations
batiments = ox.features_from_place(lieu, tags={"building": True})

# Vérifier les colonnes disponibles
print("📌 Colonnes disponibles :", batiments.columns)

# Afficher les noms et autres infos disponibles
if "name" in batiments.columns:
    print("🏛️ Liste des bâtiments avec noms :")
    print(batiments[["name", "alt_name", "short_name", "image", "website", "source"]].dropna())
else:
    print("❌ Aucun nom trouvé pour les bâtiments.")