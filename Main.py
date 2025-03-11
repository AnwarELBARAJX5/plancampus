from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy.clock import Clock
import os
import DatabaseManager
import itineraire
from kivymd.uix.menu import MDDropdownMenu
import sqlite3

# 📌 Interface utilisateur
KV = """
BoxLayout:
    orientation: 'vertical'
    
    MDTopAppBar:
        title: 'Carte Kivy'
        size_hint_y: 0.1  

    MapView:
        id: mapview
        lat: 43.305446
        lon: 5.377284
        zoom: 18
        size_hint: 1, 1  

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.2  
        padding: 10
        spacing: 5

    MDTextField:
        id: start_location
        hint_text: "Point de départ (bâtiment, salle ou coordonnées)"
        mode: "rectangle"
        on_text: app.show_suggestions(self.text, "start")

    MDTextField:
        id: end_location
        hint_text: "Destination (bâtiment, salle ou coordonnées)"
        mode: "rectangle"
        on_text: app.show_suggestions(self.text, "end")

    Button:
        text: "Trouver l'itinéraire"
        size_hint_y: None
        height: 40
        on_release: app.calculate_route()
"""

class Main(MDApp):
    def build(self):
        # 🔹 Supprimer l'ancien itinéraire au démarrage
        route_file = os.path.join(os.getcwd(), "batgeojson/itineraire_valhalla.geojson")
        if os.path.exists(route_file):
            os.remove(route_file)
            print("🗑 Ancien itinéraire supprimé au démarrage.")

        self.screen = Builder.load_string(KV)
        self.mapview = self.screen.ids.mapview
        self.geojson_layers = []  
        self.route_layer = None

        # 📌 Gestion des menus de suggestions
        self.menu_start = None
        self.menu_end = None
        self.current_menu = None  # Stocker le menu actif

        # 📌 Charger les fichiers GeoJSON des bâtiments
        self.load_geojson_layers("batgeojson")

        # 📌 Animation clignotante pour les bâtiments
        Clock.schedule_interval(self.toggle_opacity, 0.5)

        return self.screen

    def load_geojson_layers(self, directory):
        """Charge tous les fichiers GeoJSON d'un dossier."""
        path = os.path.join(os.getcwd(), directory)
        if not os.path.exists(path):
            print(f"⚠️ Dossier introuvable : {directory}")
            return

        files = [f for f in os.listdir(path) if f.endswith('.geojson')]
        for file in files:
            geojson_file = os.path.join(path, file)
            geojson_layer = GeoJsonMapLayer(source=geojson_file)
            geojson_layer.opacity = 1
            self.mapview.add_widget(geojson_layer)
            self.geojson_layers.append(geojson_layer)

    def toggle_opacity(self, dt):
        """Alterner l’opacité entre 0 et 1 pour chaque bâtiment GeoJSON."""
        for layer in self.geojson_layers:
            layer.opacity = 0 if layer.opacity == 1 else 1

    def show_suggestions(self, text, field):
        """Affiche les suggestions de bâtiments/salles lors de la saisie."""
        if not text:
            return  # Ne rien faire si l'entrée est vide

        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor

        # 🔹 Recherche partielle des bâtiments et salles
        query = f"%{text.lower()}%"
        cursor.execute("SELECT nom FROM Batiment WHERE LOWER(nom) LIKE ?", (query,))
        results = cursor.fetchall()

        cursor.execute("SELECT numsalle FROM Etage WHERE LOWER(numsalle) LIKE ?", (query,))
        results += cursor.fetchall()
        
        db.close()

        # 🔹 Création des suggestions
        suggestions = [
            {"text": result[0], "on_release": lambda x=result[0], f=field: self.select_suggestion(x, f)}
            for result in results
        ]

        # **Correction : fermer l'ancien menu avant d'en ouvrir un nouveau**
        if self.current_menu:
            self.current_menu.dismiss()
            self.current_menu = None  # Réinitialiser après fermeture

        # 🔹 Déterminer quel menu utiliser
        if field == "start":
            self.menu_start = MDDropdownMenu(caller=self.screen.ids.start_location, items=suggestions, width_mult=4)
            menu = self.menu_start
        else:
            self.menu_end = MDDropdownMenu(caller=self.screen.ids.end_location, items=suggestions, width_mult=4)
            menu = self.menu_end

        # 🔹 Mettre à jour et ouvrir le menu
        menu.items = suggestions
        menu.open()

        # 🔹 Sauvegarde du menu actif
        self.current_menu = menu

    def select_suggestion(self, name, field):
        """Remplit le champ avec la suggestion sélectionnée."""
        if field == "start":
            self.screen.ids.start_location.text = name
            if self.menu_start:
                self.menu_start.dismiss()
        else:
            self.screen.ids.end_location.text = name
            if self.menu_end:
                self.menu_end.dismiss()

        self.current_menu = None  # Réinitialiser après fermeture

    def calculate_route(self):
        start_text = self.screen.ids.start_location.text.strip()
        end_text = self.screen.ids.end_location.text.strip()

        db = DatabaseManager.DatabaseManager()
        db.connect()

        # 🔹 Vérifier si l'utilisateur a entré une adresse ou un bâtiment/salle
        start_location = DatabaseManager.get_location_from_db(start_text) if not "," in start_text else tuple(map(float, start_text.split(",")))
        end_location = DatabaseManager.get_location_from_db(end_text) if not "," in end_text else tuple(map(float, end_text.split(",")))

        db.close()

        if not start_location or not end_location:
            print("❌ Erreur : L'un des lieux est introuvable.")
            return

        start = [start_location[0], start_location[1]]
        end = [end_location[0], end_location[1]]

        # 🔹 Générer l'itinéraire avec Valhalla
        path = os.path.join(os.getcwd(), "batgeojson")
        filename = os.path.join(path, "itineraire_valhalla.geojson")
        itineraire.get_valhalla_route(start, end, filename)

        # 🔹 Afficher la route sur la carte
        self.add_route_to_map(filename)

    def add_route_to_map(self, geojson_file):
        """Ajoute un itinéraire GeoJSON à la carte en supprimant l'ancien s'il existe"""
        # 🔹 Supprimer l'ancien itinéraire s'il y en a un
        if self.route_layer:
            print("🗑 Suppression de l'ancien itinéraire")
            self.mapview.remove_widget(self.route_layer)

        # 🔹 Vérifier si le fichier existe
        if os.path.exists(geojson_file):
            print(f"📌 Chargement du fichier GeoJSON : {geojson_file}")
            self.route_layer = GeoJsonMapLayer(source=geojson_file)
            self.mapview.add_widget(self.route_layer)
            print("✅ Itinéraire ajouté sur la carte")
        else:
            print(f"⚠️ Erreur : fichier GeoJSON introuvable ({geojson_file})")

if __name__ == "__main__":
    Main().run()
