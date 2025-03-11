import sqlite3
from Batiment import Batiment
# Classe DatabaseManager pour gérer la base de données SQLite
class DatabaseManager:
    def __init__(self, db_name="batiments.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Établit la connexion à la base de données SQLite."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Crée les tables Batiment et Etage si elles n'existent pas."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Batiment (
                numbat INTEGER PRIMARY KEY,
                nom TEXT,
                nbetage INTEGER,
                long NUMERIC,
                lat NUMERIC
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Etage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numbat INTEGER,
                numsalle TEXT,
                long NUMERIC,
                lat NUMERIC,
                 FOREIGN KEY (numbat) REFERENCES Batiment(numbat)
            )
        ''')

        self.conn.commit()

    def insert_batiment(self, batiment):
        """Insère un bâtiment dans la base de données."""
        self.cursor.execute('''
            INSERT INTO Batiment (numbat, nom, nbetage)
            VALUES (?, ?, ?)
        ''', (batiment.numBat, batiment.nom, batiment.nbetage))
        self.conn.commit()

    def insert_etages(self, batiment, lon, lat):
        """Insère les salles avec leurs coordonnées GPS dans la base de données."""
        for salle_data in batiment.listesalle:
        # ✅ Extraction correcte des valeurs
            numsalle = salle_data[0]  # Numéro de salle
            salle_lon = lon  # Longitude du bâtiment
            salle_lat = lat  # Latitude du bâtiment

            self.cursor.execute('''
            INSERT INTO Etage (numbat, numsalle, long, lat)
            VALUES (?, ?, ?, ?)
            ''', (batiment.numBat, numsalle, salle_lon, salle_lat))

        self.conn.commit()

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()

# Fonction externe pour générer et afficher les salles d'un bâtiment et les insérer dans la base de données
def generer_salles_batiment(numBat, salleParetage, dic,indices_depart=None):
    """
    Génère les salles d'un bâtiment, assigne les adresses et insère les données dans la base.

    📌 Paramètres :
    - numBat (int) : Numéro du bâtiment
    - salleParetage (list) : Structure des salles
    - dic (dict) : Dictionnaire contenant {batX: "lon, lat"}
    - indices_depart (list, optionnel) : Indices de départ pour les numéros de salles
    """

    # ✅ Récupérer les coordonnées (lon, lat) du bâtiment
    coords = extract_adresse(dic, numBat)
    if not coords:
        print(f"⚠️ Aucune adresse trouvée pour le bâtiment {numBat} !")
        return
    
    lon, lat = coords  # 📌 Décomposer en longitude & latitude

    # ✅ Créer une instance du bâtiment
    batiment = Batiment(numBat, salleParetage, indices_depart)

    # ✅ Générer les salles
    batiment.generationlistesalle()

    # ✅ Ajouter les coordonnées du bâtiment à chaque salle
    for i in range(len(batiment.listesalle)):  # 🔄 Correction ici
        salle = batiment.listesalle[i]
        batiment.listesalle[i] = (salle, lon, lat)  # 📌 Assigner lon & lat

    # ✅ Afficher les salles avec coordonnées
    batiment.afficher_salles()

    # ✅ Gérer la base de données
    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.create_tables()

    # ✅ Insérer le bâtiment et ses étages avec les adresses
    db_manager.insert_batiment(batiment)
    db_manager.insert_etages(batiment, lon, lat)  # 📌 Ajout des coordonnées

    # ✅ Mettre à jour les adresses des bâtiments dans la base
    inserer_adresses_bdd(dic)

    # ✅ Fermer la base de données
    db_manager.close()

    print(f"✅ Génération des salles pour le bâtiment {numBat} avec adresses terminée.")

def ajouter_salles(numbat, salles, dic):
    """
    Ajoute manuellement des salles à un bâtiment spécifique dans la base de données.

    :param numbat: Numéro du bâtiment.
    :param salles: Liste des numéros de salle à ajouter.
    :param dic: Dictionnaire contenant les adresses (longitude, latitude).
    """
    # Connexion à la base SQLite
    conn = sqlite3.connect("batiments.db")
    cursor = conn.cursor()

    for salle in salles:
        # Vérifier si la salle a ses propres coordonnées
        if salle in dic:
            salle_lon, salle_lat = map(float, dic[salle].split(", "))

            # 🔹 Insérer uniquement si les coordonnées existent
            cursor.execute("INSERT INTO Etage (numbat, numsalle, long, lat) VALUES (?, ?, ?, ?)", 
                           (numbat, salle, salle_lon, salle_lat))
        else:
            cursor.execute("INSERT INTO Etage (numbat, numsalle) VALUES (?, ?)", 
                           (numbat, salle))
            print(f"⚠️ Adresse non trouvée pour la salle '{salle}', non insérée.")

    # 🔹 Valider et fermer la connexion
    conn.commit()
    conn.close()

    print(f"✅ Les salles {salles} ont été ajoutées au bâtiment {numbat} avec succès avec coordonnées GPS.")

def bat_adresse(bat):
    """Récupère l'adresse d'un bâtiment en fonction de son numéro."""
    conn = sqlite3.connect("batiments.db")
    cursor = conn.cursor()
    cursor.execute("SELECT adress FROM batiments WHERE numbat=?", (bat))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None  

def salle_adresse(salle):
    """Récupère l'adresse d'un bâtiment en fonction de son numéro."""
    conn = sqlite3.connect("batiments.db")
    cursor = conn.cursor()
    cursor.execute("SELECT adress FROM Etage WHERE numsalle=?", (salle))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None  

"""def  ajouter_adress(key,adress){
    conn = sqlite3.connect("batiments.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Batiments(numbat, numsalle) VALUES (?, ?)", (numbat, salle))
    
}"""

def extract_adresse(dic, numbat):
    """Récupère la longitude et latitude d'un bâtiment à partir du dictionnaire."""
    
    # Convertir le numéro de bâtiment en format "batX" -> X
    key = f"bat{numbat}"  # Si numbat = 2, key devient "bat2"
    
    if key in dic:  # Vérifie si la clé existe
        lon, lat = map(float, dic[key].split(", "))  # Sépare et convertit en float
        return [lon, lat]  # Retourne les coordonnées
    
    return None 

def inserer_adresses_bdd(dic):
    """Ajoute ou met à jour les adresses (longitude, latitude) des bâtiments dans la base de données."""

    conn = sqlite3.connect("batiments.db")  # Connexion à la base
    cursor = conn.cursor()

    for numbat in range(1, 20):  # On suppose que les bâtiments vont de 1 à 15
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


def get_location_from_db(name):
    """
    Récupère la latitude et la longitude d'un bâtiment ou d'une salle depuis la base de données.
    :param name: Nom du bâtiment, numéro du bâtiment ou numéro de salle (ex: "bat7", "7-051", "Bibliothèque").
    :return: (longitude, latitude) ou None si non trouvé.
    """
    conn = sqlite3.connect("batiments.db")
    cursor = conn.cursor()

    # 🔹 Vérifier si c'est un **numéro de bâtiment**
    cursor.execute("SELECT long, lat FROM Batiment WHERE numbat=?", (name,))
    result = cursor.fetchone()

    if not result:
        # 🔹 Vérifier si c'est un **nom de bâtiment** (ex: "Bibliothèque")
        cursor.execute("SELECT long, lat FROM Batiment WHERE LOWER(nom) = LOWER(?)", (name,))
        result = cursor.fetchone()

    if not result:
        # 🔹 Vérifier si c'est une **salle**
        cursor.execute("SELECT long, lat FROM Etage WHERE numsalle=?", (name,))
        result = cursor.fetchone()

    conn.close()
    return (result[1], result[0]) if result else None