from DatabaseManager import *
import sqlite3

generer_salles_batiment(15, [0,0, 8, 2, 13, 5],[0,1,  1, 12, 1,9])
generer_salles_batiment(5, [13,0, 13, 6],[1, 0, 1, 5])
generer_salles_batiment(7, [5,0, 7, 2],[1, 0, 0, 0]) #salle 7-05? manquante
generer_salles_batiment(6, [5],[0])
generer_salles_batiment(3, [2],[1])#salle 3-05? manquante
generer_salles_batiment(1, [],[])
generer_salles_batiment(8, [2],[1])
generer_salles_batiment(9, [1],[2]) #salle 9-05? manquante
generer_salles_batiment(14,[10,28,13],[1,0,0])
generer_salles_batiment(2,[],[])
generer_salles_batiment(13,[],[])
generer_salles_batiment(16,[],[])
generer_salles_batiment(17,[],[])

ajouter_salles(7,["7-051","7-050"])
ajouter_salles(6,["Bibliotèque Universitaire"])
ajouter_salles(2,["Grand Amphi"])
ajouter_salles(3,["3-050","3-051","3-052"])
ajouter_salles(5,["Amphi Fabry","Amphi Perès","Amphi Marion","Amphi Lavoisier"])
ajouter_salles(8,["Amphi Sciences Naturelles"])
ajouter_salles(9,["Amphi Charve","9-051","9-050"])
ajouter_salles(7,["Amphi Massiani"])
ajouter_salles(13,["Gymnase"])
ajouter_salles(16,["Restaurant Universitaire"])
ajouter_salles(17,["Cité Universitaire"])


dico_adresse = {
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
    "Cafe": "43.305260, 5.377628",
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
    "Salle 7-050": "43.305604, 5.379854",
    "Salle 7-051": "43.305567, 5.379886",
    "Salle 6-001":"43.304606, 5.377008",
}

def extract_adresse(dic, numbat):
    """Récupère la longitude et latitude d'un bâtiment à partir du dictionnaire."""
    
    # Convertir le numéro de bâtiment en format "batX" -> X
    key = f"bat{numbat}"  # Si numbat = 2, key devient "bat2"
    
    if key in dic:  # Vérifie si la clé existe
        lon, lat = map(float, dic[key].split(", "))  # Sépare et convertit en float
        return [lon, lat]  # Retourne les coordonnées
    
    return None  # Retourne None si le bâtiment n'existe pas

def inserer_adresses_bdd(dic):
    """Ajoute ou met à jour les adresses (longitude, latitude) des bâtiments dans la base de données."""

    conn = sqlite3.connect("batiments.db")  # Connexion à la base
    cursor = conn.cursor()

    for numbat in range(1, 16):  # On suppose que les bâtiments vont de 1 à 15
        coords = extract_adresse(dic, numbat)  # Récupérer les coordonnées [long, lat]
        
        if coords:
            lon, lat = coords
            
            # Mise à jour des coordonnées GPS dans la base
            cursor.execute("""
                UPDATE Batiment 
                SET long = ?, lat = ?
                WHERE numbat = ?
            """, (lon, lat, numbat))
    
    conn.commit()  # Valider les modifications
    conn.close()   # Fermer la connexion
    
    print("Mise à jour des adresses effectuée avec succès !")


# Exécuter la mise à jour dans la base de données
inserer_adresses_bdd(dico_adresse)


