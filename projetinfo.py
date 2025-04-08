from DatabaseManager import DatabaseManager

# Créer une instance de DatabaseManager
db = DatabaseManager()

# Appeler la méthode via l'instance
buildings = db.get_buildings_with_rooms()
print(buildings)