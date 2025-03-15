from DatabaseManager import *
import sqlite3
import os
from DatabaseManager import DatabaseManager
dic= {
    "bat1":"43.304915, 5.378867",
    "bat2": "43.305159, 5.378041",
    "bat3": "43.305403, 5.378269",
    "bat5": "43.305707, 5.377665",
    "bat6": "43.304749, 5.377309",
    "bat7": "43.306018, 5.379723",
    "bat8": "43.305543, 5.379208",
    "bat9": "43.305071, 5.379551",
    "bat13": "43.306117, 5.377574",
    "bat14": "43.304786, 5.376601",
    "bat15": "43.306456, 5.379339",
    "Bibliotèque Universitaire": "43.304938, 5.377534",
    "Cafétaria": "43.305260, 5.377628",
    "bat16": "43.306377, 5.378258",#ru
    "bat17": "43.306390, 5.378344",#CITE U
    "Grand Amphi": "43.305204, 5.378089",
    "Salle Conf": "43.305489, 5.378199",#a ajouter
    "Salle Actes": "43.305385, 5.378529",#a ajouter
    "Amphi Charve": "43.305217, 5.379457",
    "Amphi Massiani": "43.305561, 5.379827",
    "Amphi Sciences Naturelles": "43.305553, 5.379210",
    "Amphi Fabry": "43.305512, 5.377277",
    "Amphi Peres": "43.305631, 5.377593",
    "Amphi Marion": "43.305739, 5.377810",
    "Amphi Lavoisier": "43.305871, 5.378124",
    "Gymnase": "43.306117, 5.377574",
    "Restaurant Universitaire": "43.306377, 5.378258",
    "Cité Universitaire": "43.306390, 5.378344",
    "9-051": "43.305217, 5.379457",
    "9-050": "43.305217, 5.379457",
    "7-051": "43.305604, 5.379854",
    "7-051": "43.305567, 5.379886",
    "6-001":"43.304606, 5.377008",
    "3-050": "43.305403, 5.378269",
    "3-051": "43.305403, 5.378269",
    "3-052": "43.305403, 5.378269",
}
generer_salles_batiment(15, [0,0, 8, 2, 13, 5],dic,[0,1,  1, 12, 1,9])
generer_salles_batiment(5, [13,0, 13, 6],dic,[1, 0, 1, 5])
generer_salles_batiment(7, [5,0, 7, 2],dic,[1, 0, 0, 0]) #salle 7-05? manquante
generer_salles_batiment(6, [5],dic,[0])
generer_salles_batiment(3, [2],dic,[1])#salle 3-05? manquante
generer_salles_batiment(1, [],dic,[])
generer_salles_batiment(8, [2],dic,[1])
generer_salles_batiment(9, [1],dic,[2]) #salle 9-05? manquante
generer_salles_batiment(14,[10,28,13],dic,[1,0,0])
generer_salles_batiment(2,[],dic,[])
generer_salles_batiment(13,[],dic,[])
generer_salles_batiment(16,[],dic,[])
generer_salles_batiment(17,[],dic,[])
generer_salles_batiment(18,[],dic,[])

ajouter_salles(7,["7-051","7-050","Amphi Massiani"],dic)
ajouter_salles(6,["Bibliotèque Universitaire"],dic)
ajouter_salles(2,["Grand Amphi"],dic)
ajouter_salles(3,["3-050","3-051","3-052"],dic)
ajouter_salles(5,["Amphi Fabry","Amphi Peres","Amphi Marion","Amphi Lavoisier"],dic)
ajouter_salles(8,["Amphi Sciences Naturelles"],dic)
ajouter_salles(9,["Amphi Charve","9-051","9-050"],dic)
ajouter_salles(13,["Gymnase"],dic)
ajouter_salles(16,["Restaurant Universitaire"],dic)
ajouter_salles(17,["Cité Universitaire"],dic)
ajouter_salles(18,["Cafétaria"],dic)




# Exécuter la mise à jour dans la base de données
#inserer_adresses_bdd(dic)



db = DatabaseManager()
geojson_folder = "batgeojson"

for filename in os.listdir(geojson_folder):
    if filename.endswith(".geojson"):
        try:
            # ✅ Extraire le numéro du bâtiment correctement
            numbat = filename.replace("bat", "").replace(".geojson", "")  # Ex: "bat7.geojson" → "7"
            numbat = int(numbat)  # ✅ Convertir en entier
            
            # ✅ Construire le chemin complet du fichier
            geojson_path = os.path.join(geojson_folder, filename)
            
            # ✅ Insérer le chemin dans la base
            db.insert_geojson_path(numbat, geojson_path)
            print(f"✅ Fichier ajouté : {geojson_path} → Bâtiment {numbat}")

        except ValueError:
            print(f"⚠️ Fichier ignoré : {filename} (nom non valide)")