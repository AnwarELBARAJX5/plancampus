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
from kivymd.uix.list import OneLineListItem
import sqlite3

# 📌 Interface utilisateur
KV = """BoxLayout:
    orientation: 'vertical'
    
    MDTopAppBar:
        title: 'Carte Kivy'
        size_hint_y: 0.1  

    MapView:
        id: mapview
        lat: 43.305446
        lon: 5.377284
        zoom: 18
        size_hint: 1, 0.45  # 📌 Encore un peu plus petit pour laisser de la place

    ScrollView:
        size_hint_y: 0.3  # 📌 Augmente la hauteur de la liste des directions
        MDList:
            id: directions_list

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.25  # 📌 Augmenter la hauteur du champ de saisie pour équilibrer
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
    

        # 📌 Animation clignotante pour les bâtiments
        Clock.schedule_interval(self.toggle_opacity, 0.5)

        return self.screen
    
    def load_geojson_layers(self, numbat):
        """Affiche uniquement le bâtiment de destination sur la carte."""

        # 🔹 Supprimer les anciens bâtiments affichés
        for layer in self.geojson_layers:
            self.mapview.remove_widget(layer)
        self.geojson_layers.clear()

        # 🔹 Connexion à la base de données pour récupérer le chemin GeoJSON
        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor

        cursor.execute("SELECT geojson_path FROM Batiment WHERE numbat = ?", (numbat,))
        result = cursor.fetchone()

        db.close()

        if result and result[0]:  # Si un chemin GeoJSON est trouvé
            geojson_path = os.path.join(os.getcwd(), result[0])  # Ajout du chemin absolu

            if os.path.exists(geojson_path):
                geojson_layer = GeoJsonMapLayer(source=geojson_path)
                geojson_layer.opacity = 1  # Assurer la visibilité
                self.mapview.add_widget(geojson_layer)
                self.geojson_layers.append(geojson_layer)
                print(f"✅ Bâtiment {numbat} affiché depuis {geojson_path}.")
            else:
                print(f"⚠️ Le fichier GeoJSON {geojson_path} n'existe pas.")
        else:
            print(f"⚠️ Aucun fichier GeoJSON trouvé en base pour le bâtiment {numbat}.")

    
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
        """Calcule et affiche l'itinéraire en fonction des entrées de l'utilisateur."""
        
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

        # 🔹 Détecter si l'utilisateur a entré un bâtiment ou une salle
        destination_batiment = None

        if end_text.lower().startswith("bâtiment"):
            try:
                destination_batiment = int(end_text.replace("Bâtiment", "").strip())
            except ValueError:
                print(f"⚠️ Impossible d'extraire le numéro de bâtiment depuis '{end_text}'.")
        
        elif end_text.lower().startswith("bat"):
            try:
                destination_batiment = int(end_text.replace("bat", "").strip())
            except ValueError:
                print(f"⚠️ Impossible d'extraire le numéro de bâtiment depuis '{end_text}'.")

        else:
            # 🔹 Si l'utilisateur a entré une salle, récupérer son bâtiment
            db = DatabaseManager.DatabaseManager()
            db.connect()
            cursor = db.cursor

            cursor.execute("SELECT numbat FROM Etage WHERE numsalle = ?", (end_text,))
            result = cursor.fetchone()

            db.close()

            if result:
                destination_batiment = result[0]  
                print(f"📌 La salle '{end_text}' appartient au bâtiment {destination_batiment}.")
            else:
                print(f"⚠️ Salle '{end_text}' introuvable dans la base de données.")

        # 🔹 Afficher le bâtiment destination s'il est trouvé
        if destination_batiment:
            print(f"📌 Bâtiment destination détecté : {destination_batiment}")
            self.load_geojson_layers(destination_batiment)
            Clock.schedule_once(self.mapview.do_update, 0) # ✅ Rafraîchissement de la carte
        else:
            print(f"⚠️ Aucun bâtiment détecté pour '{end_text}', pas d'affichage.")

        # 🔹 Générer l'itinéraire avec Valhalla
        path = os.path.join(os.getcwd(), "batgeojson")
        filename = os.path.join(path, "itineraire_valhalla.geojson")
        
        route_data = itineraire.get_valhalla_route(start, end, filename)

        if route_data:
            directions = route_data["directions"]
            total_distance = route_data["distance"]
            total_duration = route_data["duration"]

            print(f"✅ Distance : {total_distance} km, Durée : {total_duration:.2f} min")
            print("📌 Étapes du trajet :", directions)

            # 🔹 Affichage dynamique des instructions sur l'écran
            self.display_directions(directions, total_distance, total_duration)

            # 🔹 Afficher la route sur la carte
            self.add_route_to_map(filename)
        else:
            print("❌ Échec de récupération de l'itinéraire.")

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
        
    def display_directions(self, directions, total_distance, total_duration):
        """Affiche dynamiquement les instructions de navigation."""
        directions_list = self.screen.ids.directions_list
        directions_list.clear_widgets()  # Nettoyer les anciennes instructions

        print("📌 Mise à jour des étapes de l'itinéraire...")

        # 🔹 Ajouter la distance et la durée en haut de la liste
        directions_list.add_widget(OneLineListItem(text=f"Distance : {total_distance:.2f} km"))
        directions_list.add_widget(OneLineListItem(text=f"Durée estimée : {total_duration:.2f} min"))

        # 🔹 Ajouter chaque instruction
        for step in directions:
            print(f"Ajout de l'étape : {step}")  # 🔹 Debugging
            directions_list.add_widget(OneLineListItem(text=step))

        print("✅ Instructions mises à jour dans l'interface.")


if __name__ == "__main__":
    Main().run()
