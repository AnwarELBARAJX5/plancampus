from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
import os
import DatabaseManager
import itineraire
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
import sqlite3
from plyer import gps
# KV string intégrant un écran de chargement et l'écran principal
KV = '''
ScreenManager:
    LoadingScreen:
    SecondScreen:  # Maintenant, l'écran de recherche est l'écran principal
    MainScreen:  # Contient l'itinéraire

<LoadingScreen>:
    name: 'loading'
    
    MDFloatLayout:
        canvas.before:
            Color:
                rgba: 0.172, 0.216, 0.318, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Image:
            source: "assets/logo.png"
            size_hint: None, None
            size: 250, 250
            pos_hint: {"center_x": 0.5, "center_y": 0.6}

<SecondScreen>: 
    name: 'search'
    BoxLayout:
        orientation: 'vertical'
        
        
        MDTopAppBar:
            title: 'Plan Campus Saint-Charles'
            size_hint_y: 0.1  
            md_bg_color: 0.172, 0.216, 0.318, 1
            right_action_items: [["map", lambda x: app.switch_to_main()]]  # Bouton "Vous êtes perdu ?"
            
        MDTextField:
            id: search_field
            hint_text: "Rechercher un bâtiment..."
            mode: "rectangle"
            size_hint_x: 0.7
            pos_hint: {"center_y": 0.5}
            on_text: app.show_suggestions_search(self.text)

        MDRaisedButton:
            text: "Confirmer"
            size_hint_x: 0.3
            md_bg_color: 0.172, 0.216, 0.318, 1
            on_release: app.show_suggestions_search(app.screen_manager.get_screen('search').ids.search_field.text, confirm=True)

        MapView:
            id: mapview_search
            lat: 43.305446
            lon: 5.377284
            zoom: 18
            size_hint: 1, 0.45
        
        MDFillRoundFlatButton:
            text: "VOUS ÊTES PERDU ?"
            size_hint_x: 1
            md_bg_color: 0.172, 0.216, 0.318, 1  # Couleur de fond
            text_color: 1, 1, 1, 1  # Texte blanc
            font_size: "16sp"
            theme_text_color: "Custom"
            valign: "center"
            halign: "left"
            padding: [dp(15), 0, 0, 0]  # Ajuste l'espace pour l'icône à droite
            on_release: app.switch_to_main()
            on_release: app.activate_gps()

            IconRightWidget:
                icon: "navigation"  # Icône de localisation
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1  # Icône en blanc
                pos_hint: {"x": 0.9}

<MainScreen>:  # L'écran de l'itinéraire devient secondaire
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: 'VOUS ÊTES PERDU ?'
            size_hint_y: 0.1  
            md_bg_color: 0.172, 0.216, 0.318, 1
            left_action_items: [["arrow-left", lambda x: app.switch_to_search()]]  # Bouton retour

        MapView:
            id: mapview
            lat: 43.305446
            lon: 5.377284
            zoom: 18
            size_hint: 1, 0.45

        ScrollView:
            size_hint_y: 0.3
            MDList:
                id: directions_list

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.25
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

            MDRaisedButton:
                text: "Trouver l'itinéraire"
                size_hint_y: None
                height: 40
                on_release: app.calculate_route()

'''

# Définir les écrans comme des classes (optionnel, mais utile pour des personnalisations futures)
class LoadingScreen(Screen):
    pass

class MainScreen(Screen):
    pass
class SecondScreen(Screen):
    pass
class Main(MDApp):
    def build(self):
        # 🔹 Supprimer l'ancien itinéraire au démarrage
        self.screen_manager = Builder.load_string(KV)
        
        # Récupérer les écrans modifiés
        self.search_screen = self.screen_manager.get_screen('search')
        self.main_screen = self.screen_manager.get_screen('main')

        self.mapview_search = self.search_screen.ids.mapview_search
        self.mapview = self.main_screen.ids.mapview
        self.geojson_layers = [] 
        self.current_menu = None 
        self.route_layer = None
        Clock.schedule_once(self.switch_to_search, 5)  # Commencer avec l'écran de recherche
        
        return self.screen_manager
    
    def switch_to_main(self, dt=None):
        """🔹 Passer à l'écran de l'itinéraire"""
        self.screen_manager.current = 'main'

    def switch_to_search(self, dt=None):
        """🔹 Revenir à l'écran de recherche"""
        self.screen_manager.current = 'search'

    def load_geojson_layers(self, numbat, mapview):
        """Affiche le bâtiment recherché sur la bonne carte"""
        
        # ✅ Vérifier si la couche existe avant de la supprimer
        for layer in self.geojson_layers:
            if layer in mapview.children:  # 🔹 Vérifie si `layer` est bien dans `mapview`
                mapview.remove_widget(layer)
        
        self.geojson_layers.clear()  # ✅ Nettoyer la liste

        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor

        cursor.execute("SELECT geojson_path FROM Batiment WHERE numbat = ?", (numbat,))
        result = cursor.fetchone()
        db.close()

        if result and result[0]:
            geojson_path = os.path.join(os.getcwd(), result[0])
            if os.path.exists(geojson_path):
                geojson_layer = GeoJsonMapLayer(source=geojson_path)
                geojson_layer.opacity = 1
                mapview.add_widget(geojson_layer)
                self.geojson_layers.append(geojson_layer)  # ✅ Ajoute la couche pour éviter l'erreur
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
            return

        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor

        query = f"%{text.lower()}%"
        cursor.execute("SELECT nom FROM Batiment WHERE LOWER(nom) LIKE ?", (query,))
        results = cursor.fetchall()

        cursor.execute("SELECT numsalle FROM Etage WHERE LOWER(numsalle) LIKE ?", (query,))
        results += cursor.fetchall()
        db.close()

        suggestions = [
            {"text": result[0], "on_release": lambda x=result[0], f=field: self.select_suggestion(x, f)}
            for result in results
        ]

        if self.current_menu:
            self.current_menu.dismiss()
            self.current_menu = None

        if field == "start":
            self.menu_start = MDDropdownMenu(caller=self.main_screen.ids.start_location, items=suggestions, width_mult=4)
            menu = self.menu_start
        else:
            self.menu_end = MDDropdownMenu(caller=self.main_screen.ids.end_location, items=suggestions, width_mult=4)
            menu = self.menu_end

        menu.items = suggestions
        menu.open()
        self.current_menu = menu

    def select_suggestion(self, name, field):
        if field == "start":
            self.main_screen.ids.start_location.text = name
            if self.menu_start:
                self.menu_start.dismiss()
        else:
            self.main_screen.ids.end_location.text = name
            if self.menu_end:
                self.menu_end.dismiss()

        self.current_menu = None

    def calculate_route(self):
        """Calcule et affiche l'itinéraire en fonction des entrées de l'utilisateur."""
        start_text = self.main_screen.ids.start_location.text.strip()
        end_text = self.main_screen.ids.end_location.text.strip()

        db = DatabaseManager.DatabaseManager()
        db.connect()

        start_location = DatabaseManager.get_location_from_db(start_text) if "," not in start_text else tuple(map(float, start_text.split(",")))
        end_location = DatabaseManager.get_location_from_db(end_text) if "," not in end_text else tuple(map(float, end_text.split(",")))

        db.close()

        if not start_location or not end_location:
            print("❌ Erreur : L'un des lieux est introuvable.")
            return

        start = [start_location[0], start_location[1]]
        end = [end_location[0], end_location[1]]

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

        if destination_batiment:
            print(f"📌 Bâtiment destination détecté : {destination_batiment}")
            self.load_geojson_layers(destination_batiment,self.mapview)
            Clock.schedule_once(self.mapview.do_update, 0)
        else:
            print(f"⚠️ Aucun bâtiment détecté pour '{end_text}', pas d'affichage.")

        path = os.path.join(os.getcwd(), "batgeojson")
        filename = os.path.join(path, "itineraire_valhalla.geojson")
        route_data = itineraire.get_valhalla_route(start, end, filename)

        if route_data:
            directions = route_data["directions"]
            total_distance = route_data["distance"]
            total_duration = route_data["duration"]

            print(f"✅ Distance : {total_distance} km, Durée : {total_duration:.2f} min")
            print("📌 Étapes du trajet :", directions)
            self.display_directions(directions, total_distance, total_duration)
            self.add_route_to_map(filename)
        else:
            print("❌ Échec de récupération de l'itinéraire.")

    def add_route_to_map(self, geojson_file):
        if self.route_layer:
            print("🗑 Suppression de l'ancien itinéraire")
            self.mapview.remove_widget(self.route_layer)

        if os.path.exists(geojson_file):
            print(f"📌 Chargement du fichier GeoJSON : {geojson_file}")
            self.route_layer = GeoJsonMapLayer(source=geojson_file)
            self.mapview.add_widget(self.route_layer)
            print("✅ Itinéraire ajouté sur la carte")
        else:
            print(f"⚠️ Erreur : fichier GeoJSON introuvable ({geojson_file})")
        
    def display_directions(self, directions, total_distance, total_duration):
        directions_list = self.main_screen.ids.directions_list
        directions_list.clear_widgets()
        print("📌 Mise à jour des étapes de l'itinéraire...")
        directions_list.add_widget(OneLineListItem(text=f"Distance : {total_distance:.2f} km"))
        directions_list.add_widget(OneLineListItem(text=f"Durée estimée : {total_duration:.2f} min"))

        for step in directions:
            print(f"Ajout de l'étape : {step}")
            directions_list.add_widget(OneLineListItem(text=step))
        print("✅ Instructions mises à jour dans l'interface.")

    def show_suggestions_search(self, text, confirm=False):
        """🔍 Recherche de bâtiment"""
        if not text:
            return

        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor

        query = f"%{text.lower()}%"
        cursor.execute("SELECT numbat, nom FROM Batiment WHERE LOWER(nom) LIKE ?", (query,))
        results = cursor.fetchall()
        db.close()

        if not results:
            return

        if confirm:
            selected_building = results[0][0]
            print(f"✅ Confirmation du bâtiment {selected_building}")

            self.load_geojson_layers(selected_building, self.mapview_search)
            Clock.schedule_once(self.mapview_search.do_update, 1)

            return

        if hasattr(self, "search_menu") and self.search_menu:
            self.search_menu.dismiss()

        self.search_menu = MDDropdownMenu(
            caller=self.search_screen.ids.search_field,
            items=[
                {
                    "text": f"{result[1]} (Bâtiment {result[0]})",
                    "on_release": lambda x=result: self.select_building(x)
                }
                for result in results
            ],
            width_mult=4
        )

        self.search_menu.open()


    def select_building(self, result):
        """Sélectionne un bâtiment et met le texte dans le champ de recherche."""
        screen = self.screen_manager.get_screen('search')  # 📌 On prend l'écran de recherche
        if hasattr(screen.ids, "search_field"):
            screen.ids.search_field.text = result[1]  # ✅ Met à jour la barre de recherche
            print(f"📌 Sélectionné : {result[1]}")
        
        self.search_menu.dismiss()



    def activate_gps(self):
        try:
            gps.configure(on_location=self.on_gps_location)
            gps.start()
            print("📡 GPS activé")
        except NotImplementedError:
            print("❌ GPS non disponible sur cette plateforme.")

    def on_gps_location(self, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']
        print(f"📍 Position actuelle : {lat}, {lon}")

        # On injecte dans le champ start_location
        self.main_screen.ids.start_location.text = f"{lat},{lon}"

        # Tu peux aussi centrer la carte dessus
        self.mapview.center_on(lat, lon)
        
        # (Optionnel) ajouter un marqueur
        marker = MapMarker(lat=lat, lon=lon)
        self.mapview.add_marker(marker)

if __name__ == "__main__":
        Main().run()
