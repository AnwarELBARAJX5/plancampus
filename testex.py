import pandas as pd
import os
import geojson
import Batiment

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


Batiment.generer_salles_batiment(15, [0,0, 8, 2, 13, 5],[0,1,  1, 12, 1,9])
Batiment.generer_salles_batiment(5, [13,0, 13, 6],[1, 0, 1, 5])
Batiment.generer_salles_batiment(7, [6,0, 6, 2],[0, 0, 0, 0])
Batiment.generer_salles_batiment(2,"bu")