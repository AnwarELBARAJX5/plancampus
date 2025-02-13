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
                nbetage INTEGER
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Etage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numbat INTEGER,
                numsalle TEXT,
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

    def insert_etages(self, batiment):
        """Insère les étages et leurs salles dans la base de données."""
        for etage, salle in enumerate(batiment.listesalle, start=1):
            numsalle = salle
            self.cursor.execute('''
                INSERT INTO Etage (numbat, numsalle)
                VALUES (?, ?)
            ''', (batiment.numBat, numsalle))
        self.conn.commit()

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()

# Fonction externe pour générer et afficher les salles d'un bâtiment et les insérer dans la base de données
def generer_salles_batiment(numBat, salleParetage, indices_depart=None):
    # Créer une instance du bâtiment
    batiment = Batiment(numBat, salleParetage, indices_depart)
    
    # Générer les salles
    batiment.generationlistesalle()
    
    # Afficher les salles
    batiment.afficher_salles()
    
    # Gérer la base de données
    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.create_tables()

    # Insérer le bâtiment et ses étages dans la base de données
    db_manager.insert_batiment(batiment)
    db_manager.insert_etages(batiment)

    # Fermer la base de données
    db_manager.close()


# Utilisation de la fonction externe pour générer et afficher les salles, puis insérer dans la base de données

generer_salles_batiment(15, [0,0, 8, 2, 13, 5],[0,1,  1, 12, 1,9])
generer_salles_batiment(5, [13,0, 13, 6],[1, 0, 1, 5])
generer_salles_batiment(7, [6,0, 6, 2],[0, 0, 0, 0])
generer_salles_batiment(6, [6,1, 6, 2],[0, 0, 0, 0])
