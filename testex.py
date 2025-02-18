import pandas as pd
import os
import geojson
import Batiment
import DatabaseManager
from DatabaseManager import *


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

generer_salles_batiment(15, [0,0, 8, 2, 13, 5],[0,1,  1, 12, 1,9])
generer_salles_batiment(5, [13,0, 13, 6],[1, 0, 1, 5])
generer_salles_batiment(7, [5,0, 7, 2],[1, 0, 0, 0]) #salle 7-05? manquante
generer_salles_batiment(6, [5],[0])
generer_salles_batiment(3, [2],[1])#salle 3-05? manquante
generer_salles_batiment(1, [1],[0])
generer_salles_batiment(8, [2],[1])
generer_salles_batiment(9, [1],[2]) #salle 9-05? manquante
generer_salles_batiment(14,[10,28,13],[1,0,0])
generer_salles_batiment(2,[],[])
ajouter_salles(7,["7-051","7-050"])
ajouter_salles(6,["Bibliotèque Universitaire"])
ajouter_salles(2,["Grand Amphi"])
ajouter_salles(5,["Amphi Fabry","Amphi Perès","Amphi Marion","Amphi Lavoisier"])
ajouter_salles(8,["Amphi Sciences Naturelles"])
ajouter_salles(9,["Amphi Charve","9-051","9-050"])
ajouter_salles(7,["Amphi Massiani"])