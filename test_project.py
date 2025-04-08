import unittest
import os
import tempfile
import json
import polyline
from unittest.mock import patch, MagicMock

# Importer les fonctions et classes à tester
from itineraire import get_valhalla_route
from DatabaseManager import DatabaseManager
from geojson import get_geojson_files, path as geojson_path_function
from DatabaseManager import extract_adresse
from geojson import path_suffixe
import sqlite3
import os
from DatabaseManager import get_location_from_db

# Pour tester les méthodes d'insertion de la base, on définit une classe fictive simulant un bâtiment.
class DummyBatiment:
    def __init__(self, numBat, nom, nbetage, listesalle):
        self.numBat = numBat
        self.nom = nom
        self.nbetage = nbetage
        self.listesalle = listesalle  # Doit être une liste de tuples (numsalle, lon, lat)

class TestItineraire(unittest.TestCase):
    @patch('itineraire.requests.post')
    def test_get_valhalla_route_success(self, mock_post):
        # Préparer une réponse simulée de l'API Valhalla
        # On encode une polyline avec 2 points connus
        coordinates = [(43.304599, 5.378129), (43.306456, 5.379358)]
        encoded_poly = polyline.encode(coordinates)
        fake_response_json = {
            "trip": {
                "legs": [{
                    "shape": encoded_poly,
                    "maneuvers": [{"instruction": "Aller tout droit"}]
                }],
                "summary": {"length": 1.0, "time": 600}  # 600 secondes = 10 minutes
            }
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fake_response_json
        mock_post.return_value = mock_response

        # Utiliser un répertoire temporaire pour le fichier GeoJSON
        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = os.path.join(tmpdirname, "test_itineraire.geojson")
            result = get_valhalla_route([5.378129, 43.304599], [5.379358, 43.306456], filename=filename)
            # Vérifier que le résultat est un dictionnaire avec les clés attendues
            self.assertIsNotNone(result)
            self.assertIn("geojson", result)
            self.assertIn("directions", result)
            self.assertIn("distance", result)
            self.assertIn("duration", result)
            # Vérifier que le fichier GeoJSON a bien été créé
            self.assertTrue(os.path.exists(filename))
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertEqual(data.get("type"), "FeatureCollection")
    
    @patch('itineraire.requests.post')
    def test_get_valhalla_route_failure(self, mock_post):
        # Simuler une réponse d'erreur de l'API (status != 200)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        result = get_valhalla_route([5.378129, 43.304599], [5.379358, 43.306456])
        self.assertIsNone(result)

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Utiliser une base de données en mémoire pour éviter d'écrire sur disque
        self.db = DatabaseManager(db_name=":memory:")
        self.db.connect()
        self.db.create_tables()
    
    def tearDown(self):
        self.db.close()
    
    def test_insert_batiment_and_etages(self):
        # Créer un bâtiment fictif avec deux salles
        dummy = DummyBatiment(numBat=1, nom="TestBatiment", nbetage=2,
                            listesalle=[("Salle1", 1.0, 1.0), ("Salle2", 2.0, 2.0)])
        self.db.insert_batiment(dummy)
        self.db.insert_etages(dummy, 1.0, 1.0)
        
        # Utiliser directement la connexion déjà établie
        cursor = self.db.cursor
        cursor.execute("SELECT numbat, nom, nbetage FROM Batiment WHERE numbat = ?", (1,))
        batiment_row = cursor.fetchone()
        self.assertIsNotNone(batiment_row)
        self.assertEqual(batiment_row[0], 1)
        self.assertEqual(batiment_row[1], "TestBatiment")
        self.assertEqual(batiment_row[2], 2)
        
        # Vérifier l'insertion dans la table Etage (2 enregistrements attendus)
        cursor.execute("SELECT numsalle, long, lat FROM Etage WHERE numbat = ?", (1,))
        etage_rows = cursor.fetchall()
        self.assertEqual(len(etage_rows), 2)


class TestGeojsonFunctions(unittest.TestCase):
    def setUp(self):
        # Créer un répertoire temporaire contenant des fichiers .geojson et d'autres types
        self.test_dir = tempfile.TemporaryDirectory()
        self.geojson_file1 = os.path.join(self.test_dir.name, "test1.geojson")
        self.geojson_file2 = os.path.join(self.test_dir.name, "test2.geojson")
        self.txt_file = os.path.join(self.test_dir.name, "not_a_geojson.txt")
        with open(self.geojson_file1, "w") as f:
            f.write("{}")
        with open(self.geojson_file2, "w") as f:
            f.write("{}")
        with open(self.txt_file, "w") as f:
            f.write("Not geojson")
    
    def tearDown(self):
        self.test_dir.cleanup()
    
    def test_get_geojson_files(self):
        files = get_geojson_files(self.test_dir.name)
        self.assertIn("test1.geojson", files)
        self.assertIn("test2.geojson", files)
        self.assertNotIn("not_a_geojson.txt", files)
    
    def test_path_function(self):
        full_paths = geojson_path_function(self.test_dir.name)
        expected_paths = [
            os.path.join(self.test_dir.name, "test1.geojson"),
            os.path.join(self.test_dir.name, "test2.geojson")
        ]
        self.assertCountEqual(full_paths, expected_paths)


class TestAdditionalFunctions(unittest.TestCase):
    def test_extract_adresse_found(self):
        # On prépare un dictionnaire avec une adresse pour le bâtiment 3
        dic = {"bat3": "43.305403, 5.378269"}
        self.assertEqual(extract_adresse(dic, 3), [43.305403, 5.378269],
                         "La fonction doit retourner les coordonnées pour un bâtiment existant.")
    
    def test_extract_adresse_not_found(self):
        # Lorsque le bâtiment demandé n'est pas dans le dictionnaire, la fonction doit renvoyer None
        dic = {"bat3": "43.305403, 5.378269"}
        self.assertIsNone(extract_adresse(dic, 4),
                          "La fonction doit retourner None si le bâtiment n'est pas trouvé.")
    
    def test_path_suffixe_true(self):
        # Vérifier que la fonction identifie correctement le suffixe d'un chemin (avec le séparateur Windows)
        self.assertTrue(path_suffixe("test.geojson", "C:\\folder\\test.geojson"),
                        "La fonction doit renvoyer True si le nom de fichier correspond.")
    
    def test_path_suffixe_false(self):
        # Vérifier que la fonction renvoie False si le nom de fichier ne correspond pas
        self.assertFalse(path_suffixe("test.geojson", "C:\\folder\\other.geojson"),
                         "La fonction doit renvoyer False si le nom de fichier ne correspond pas.")
        
class TestGetLocationFromDB(unittest.TestCase):
    def setUp(self):
        # Création d'une base de données de test
        self.test_db = "test_batiments.db"
        self.original_connect = sqlite3.connect  # Sauvegarde de la fonction d'origine
        self.conn = self.original_connect(self.test_db)
        cursor = self.conn.cursor()
        # Création des tables nécessaires
        cursor.execute('''CREATE TABLE Batiment (
                numbat INTEGER PRIMARY KEY,
                nom TEXT,
                nbetage INTEGER,
                long NUMERIC,
                lat NUMERIC,
                geojson_path TEXT
            )''')
        cursor.execute('''CREATE TABLE Etage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numbat INTEGER,
                numsalle TEXT,
                long NUMERIC,
                lat NUMERIC
            )''')
        # Insertion d'un bâtiment et d'une salle
        cursor.execute("INSERT INTO Batiment (numbat, nom, nbetage, long, lat) VALUES (?, ?, ?, ?, ?)",
                       (7, "TestBatiment", 1, 5.123, 43.123))
        cursor.execute("INSERT INTO Etage (numbat, numsalle, long, lat) VALUES (?, ?, ?, ?)",
                       (7, "7-051", 5.124, 43.124))
        self.conn.commit()
        self.conn.close()
        # Rediriger sqlite3.connect pour utiliser notre base de test à chaque appel
        sqlite3.connect = lambda _: self.original_connect(self.test_db)
    
    def tearDown(self):
        # Restaurer sqlite3.connect et supprimer la base de test
        sqlite3.connect = self.original_connect
        os.remove(self.test_db)
    
    def test_get_location_from_batiment(self):
        # Test de la récupération d'une adresse de bâtiment via divers formats
        loc_by_num = get_location_from_db("7")
        self.assertEqual(loc_by_num, (43.123, 5.123))
        loc_by_name = get_location_from_db("TestBatiment")
        self.assertEqual(loc_by_name, (43.123, 5.123))
    
    def test_get_location_from_salle(self):
        # Test de la récupération d'une adresse pour une salle existante
        loc_salle = get_location_from_db("7-051")
        self.assertEqual(loc_salle, (43.124, 5.124))

if __name__ == '__main__':
    unittest.main()
