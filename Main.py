from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy_garden.mapview import MapView, MapMarker,MapMarkerPopup
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelThreeLine
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineListItem







import os
import DatabaseManager
import itineraire
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
import sqlite3
from unidecode import unidecode
from plyer import gps
import asyncio
from winsdk.windows.devices.geolocation import Geolocator, PositionStatus
# KV string intégrant un écran de chargement et l'écran principal
KV = '''
ScreenManager:
    LoadingScreen:
    SecondScreen:  # Écran principal pour la recherche
    MainScreen:    # Écran pour l'itinéraire
<ClickableMDBoxLayout>:
    on_release: print("MDBoxLayout cliqué!")
    # Ajoutez ici vos widgets enfants et propriétés



<LoadingScreen>:
    name: 'loading'
    MDFloatLayout:
        canvas.before:
            Color:
                rgba: 0.172, 0.216, 0.318, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # Logo de l'application
        Image:
            source: "assets/logo.png"
            size_hint: None, None
            size: 250, 250
            pos_hint: {"center_x": 0.5, "center_y": 0.6}

        # Spinner de chargement
        MDSpinner:
            size_hint: None, None
            size: dp(46), dp(46)
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            active: True
            determinate: False
            color: (1, 1, 1, 1)

<SecondScreen>:
    name: 'search'

    MDBoxLayout:
        orientation: 'vertical'


        MDTopAppBar:
            title: 'Plan Campus Saint-Charles'
            size_hint_y: None
            height: self.theme_cls.standard_increment
            md_bg_color: 0.172, 0.216, 0.318, 1
            elevation: 2
                    # Bouton "Vous êtes perdu ?"

        # Champ + bouton "Confirmer" dans une même ligne
        
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            padding: dp(5)
            spacing: dp(5)

            MDTextField:
                id: search_field
                hint_text: "Rechercher un bâtiment..."
                mode: "line"
                icon_right: "magnify"
                size_hint_x: 0.5
                on_text: app.show_suggestions_search(self.text)

            MDRaisedButton:
                text: "Confirmer"
                size_hint_x: 0.2
                md_bg_color: 0.172, 0.216, 0.318, 1
                pos_hint: {"center_x": 0.8, "center_y": 0.5}
     
                on_release: app.show_suggestions_search(search_field.text, confirm=True)

        MapView:
            id: mapview_search
            lat: 43.305446
            lon: 5.377284
            zoom: 16
            size_hint: 1, 0.45

                
            


        

        MDBoxLayout:
            size_hint_y: 0.2
            padding: [10, 0, 10, 0]
            MDCard:
                elevation: 30
                radius: [20, 20, 0, 0]
                MDScrollView:
                    do_scroll_y: True
                    do_scroll_x: False
                    MDBoxLayout:
                        size_hint_y: 1
                        orientation: "vertical"
                        MDBoxLayout:
                            size_hint_y: 0.5
                            pos_hint:{"y":0.5}
                            MDLabel:
                                text:"Bienvenue dans le campus Saint-Charles"
                                halign:"center"
                                bold:True
                        MDScrollView:
                            padding: dp(5)
                            spacing: dp(5)
                            do_scroll_y:False
                            do_scroll_x:True
                            MDBoxLayout:
                                padding: dp(10)
                                spacing: dp(10)
                                size_hint_x:1.5
                                size_hint_y:1.2
                                ClickableMDBoxLayout:
                                    on_release: app.batiment_scroll("Bu")
                                    padding:0,0,0,0
                                    orientation:"vertical"
                                    Image:
                                        source:"bu.jpg"
                                        pos_hint:{"center_x":0.5}
                                        size: 300, 300 

                                    MDLabel:
                                        text:"Bibliotèque Universitaire"
                                        font_size:20
                                        bold:True
                                        halign:"center"
                                ClickableMDBoxLayout:
                                    padding:0,0,0,0
                                    orientation:"vertical"
                                    on_release: app.batiment_scroll("amphi")
                                    Image:
                                        source:"amphisciencenaturelles.jpg"
                                        pos_hint:{"center_x":0.5}
                                    MDLabel:
                                        text:"Amphi Sciences Naturelles"
                                        font_size:20
                                        bold:True
                                        halign:"center"
                                ClickableMDBoxLayout:
                                    padding:0,0,0,0
                                    on_release: app.batiment_scroll("bat5")
                                    orientation:"vertical"
                                    Image:
                                        source:"bat5.jpg"
                                        pos_hint:{"center_x":0.5}
                                    MDLabel:
                                        text:"Batiment 5"
                                        font_size:20
                                        bold:True
                                        halign:"center"
                        BoxLayout:
                            orientation: "horizontal"
                            
                            padding: [20,20]
                            
                            MDFillRoundFlatIconButton:
                                text: "VOUS ÊTES PERDU ?"
                                size_hint_x: 1
                                md_bg_color: 0.172, 0.216, 0.318, 1
                                text_color: 1, 1, 1, 1
                                font_size: "16sp"
                                theme_text_color: "Custom"
                                icon: "navigation"
                                pos_hint: {"center_x": 0.5}
                                padding: [0, 0]
                                on_release:
                                    app.switch_to_main()
                                    app.activate_gps()


        


                                        
<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: 'VOUS ÊTES PERDU ?'
            size_hint_y: None
            height: self.theme_cls.standard_increment
            md_bg_color: 0.172, 0.216, 0.318, 1
            elevation: 6
            left_action_items: [["arrow-left", lambda x: app.switch_to_search()]]


        MDScrollView:
            id: route_info_scroll
            do_scroll_x: False
            do_scroll_y: True
            size_hint_y: None
            height: "0dp" 
            MDList:
                id: route_info_list
                size_hint_y: None
                height: self.minimum_height
                canvas.before:
                    Color:
                        rgba: 0.9, 0.9, 0.9, 1  # Fond gris clair
                    Rectangle:
                        pos: self.pos
                        size: self.size
        FloatLayout:
            MapView:
                id: mapview
                lon: 43.305446
                lat: 5.377284
                zoom: 16
                MapMarkerPopup:
                    source:"marker.png"
                    size_hint: None, None
                    size: "60dp", "60dp"
                    lon:5.405325476016812
                    lat:43.28400325355717






            MDFloatingActionButton:
                md_bg_color: 0.172, 0.216, 0.318, 1
                icon: "google-maps"
                pos_hint: {"right": 0.95, "top": 0.95}
                on_release: app.activate_gps()

            

        
    MDBoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (1, 1, 1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        adaptive_height: True
        padding: dp(2)
        spacing: dp(2)
        MDTextField:
            id: start_location
            hint_text: "Point de départ (bâtiment, salle ou coordonnées)"
            mode: "rectangle"
            icon_right: "map-marker"
            on_text: app.show_suggestions(self.text, "start")

        MDTextField:
            id: end_location
            hint_text: "Destination (bâtiment, salle ou coordonnées)"
            mode: "rectangle"
            icon_right: "map-marker-path"
            on_text: app.show_suggestions(self.text, "end")

        MDRaisedButton:
            text: "Trouver l'itinéraire"
            size_hint_y: None
            height: 40
            md_bg_color: 0.172, 0.216, 0.318, 1
            on_release: app.calculate_route()

    
'''


# Définir les écrans comme des classes (optionnel, mais utile pour des personnalisations futures)
class LoadingScreen(Screen):
    pass

class MainScreen(Screen):
    pass
class SecondScreen(Screen):
    pass

class ClickableMDBoxLayout(ButtonBehavior, MDBoxLayout):
    pass

async def get_precise_location():
        locator = Geolocator()

        if locator.location_status in [PositionStatus.NOT_AVAILABLE, PositionStatus.DISABLED]:
            print("⚠️ Localisation désactivée ou non disponible.")
            return None

        pos = await locator.get_geoposition_async()
        coord = pos.coordinate
        return coord.point.position.longitude,coord.point.position.latitude
class main(MDApp):
    def build(self):
        # 🔹 Supprimer l'ancien itinéraire au démarrage
        self.screen_manager = Builder.load_string(KV)
        self.gps_marker = None
        # Récupérer les écrans modifiés
        self.search_screen = self.screen_manager.get_screen('search')
        self.main_screen = self.screen_manager.get_screen('main')

        self.mapview_search = self.search_screen.ids.mapview_search
        self.mapview = self.main_screen.ids.mapview
        self.geojson_layers = [] 
        self.current_menu = None 
        self.route_layer = None
        Clock.schedule_once(self.switch_to_search, 3)  # Commencer avec l'écran de recherche
        
        return self.screen_manager
    
    def switch_to_main(self, dt=None):
        """🔹 Passer à l'écran de l'itinéraire"""
        self.screen_manager.current = 'main'
        
        Clock.schedule_once(lambda dt: self.mapview.center_on(43.305446, 5.377284), 0.1)
        Clock.schedule_once(self.mapview.do_update, 0.1)



    def switch_to_search(self, dt=None):
        """🔹 Revenir à l'écran de recherche"""
        self.screen_manager.current = 'search'
    def switch_screen(self, screen_name):
        self.root.current = screen_name

    def load_geojson_layers(self, numbat, mapview):
        """Charge le GeoJSON du bâtiment et centre la carte sur ses coordonnées."""
        
        # Supprimer les anciennes couches
        for layer in self.geojson_layers:
            if layer in mapview.children:
                mapview.remove_widget(layer)
        self.geojson_layers.clear()

        # Connexion à la base
        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor
        
        # Sélectionner lat, long et geojson_path
        # Remarque : "long" est un mot-clé pour certains SGBD ou langages,
        #            si besoin, encadrez-le avec des guillemets inversés (`long`) ou renommez la colonne.
        cursor.execute("SELECT lat, `long`, geojson_path FROM Batiment WHERE numbat = ?", (numbat,))
        result = cursor.fetchone()
        db.close()

        if not result:
            print(f"⚠️ Aucun enregistrement trouvé pour le bâtiment {numbat}.")
            return

        lat_, long_, geojson_path = result
        print(f"✅ Coordonnées du bâtiment {numbat} : lat={lat_}, long={long_}")

        # Charger la couche GeoJSON si le fichier existe
        geojson_path = os.path.join(os.getcwd(), geojson_path)
        if os.path.exists(geojson_path):
            geojson_layer = GeoJsonMapLayer(source=geojson_path)
            geojson_layer.opacity = 1
            mapview.add_widget(geojson_layer)
            self.geojson_layers.append(geojson_layer)
            print(f"✅ Bâtiment {numbat} affiché depuis {geojson_path}.")
        else:
            print(f"⚠️ Le fichier GeoJSON {geojson_path} n'existe pas.")
            return

        # Centrer la carte sur les coordonnées récupérées
        # Assurez-vous que lat_ et long_ soient bien des float
        mapview.center_on(float(long_), float(lat_))
        # Eventuellement, forcer la mise à jour de la MapView
        Clock.schedule_once(mapview.do_update, 0)

    def toggle_opacity(self, dt):
        """Alterner l’opacité entre 0 et 1 pour chaque bâtiment GeoJSON."""
        for layer in self.geojson_layers:
            layer.opacity = 0 if layer.opacity == 1 else 1

    def show_suggestions(self, text, field):
        """Affiche les suggestions de bâtiments/salles lors de la saisie, en ignorant les accents."""
        if not text:
            return

        # On normalise la chaîne de recherche pour supprimer les accents
        text_normalized = unidecode(text.lower())

        db = DatabaseManager.DatabaseManager()
        db.connect()
        cursor = db.cursor

        # On récupère tous les noms de bâtiment et de salle (ou on peut faire un premier filtrage en SQL si vous voulez limiter le volume)
        cursor.execute("SELECT nom FROM Batiment")
        bat_results = cursor.fetchall()

        cursor.execute("SELECT numsalle FROM Etage")
        salle_results = cursor.fetchall()
        db.close()

        # On filtre en Python en supprimant les accents de chaque enregistrement
        results = []
        for (nom,) in bat_results:
            if text_normalized in unidecode(nom.lower()):
                results.append((nom,))
        for (numsalle,) in salle_results:
            if text_normalized in unidecode(numsalle.lower()):
                results.append((numsalle,))

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
            self.main_screen.ids.route_info_scroll.height = "105dp"
            self.add_route_to_map(filename)
            self.display_directions(
            route_data["directions"],
            route_data["distance"],
            route_data["duration"]
        )
        else:
            print("❌ Échec de récupération de l'itinéraire.")
            self.main_screen.ids.route_info_scroll.height = "0dp"

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
        route_list = self.main_screen.ids.route_info_list
        route_list.clear_widgets()
        print("📌 Mise à jour des étapes de l'itinéraire...")
        route_list.add_widget(OneLineListItem(text=f"Distance : {total_distance:.2f} km"))
        route_list.add_widget(OneLineListItem(text=f"Durée estimée : {total_duration:.2f} min"))
        for step in directions:
            print(f"Ajout de l'étape : {step}")
            route_list.add_widget(OneLineListItem(text=step))
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

    def batiment_scroll(self, bat):
        if bat == "bat5":
            self.load_geojson_layers(5, self.mapview_search)
        elif bat == "Bu":
            self.load_geojson_layers(6, self.mapview_search)
        elif bat == "amphi":
            self.load_geojson_layers(8, self.mapview_search)
        else:
            print(f"⚠️ Aucune action définie pour '{bat}'.")
        # Actualiser le MapView de l'écran courant
        Clock.schedule_once(lambda dt: self.mapview_search.do_update(dt), 1)
     





    def select_building(self, result):
        """Sélectionne un bâtiment et met le texte dans le champ de recherche."""
        screen = self.screen_manager.get_screen('search')  # 📌 On prend l'écran de recherche
        if hasattr(screen.ids, "search_field"):
            screen.ids.search_field.text = result[1]  # ✅ Met à jour la barre de recherche
            print(f"📌 Sélectionné : {result[1]}")
        
        self.search_menu.dismiss()
    def activate_gps(self):
        try:
            position = asyncio.run(get_precise_location())
            if position:
                lat, lon = position
                self.on_gps_location(lat=lat, lon=lon)
                print(f"📡 GPS précis activé : {lat}, {lon}")
                Clock.schedule_once(lambda dt: self.mapview.center_on(lon, lat), 0.1)
                Clock.schedule_once(self.mapview.do_update, 0.1)
            else:
                print("❌ Localisation indisponible.")
        except Exception as e:
            print(f"❌ Erreur de localisation : {e}")

    def on_gps_location(self, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']
        print(f"📍 Position actuelle : {lat}, {lon}")

        self.main_screen.ids.start_location.text = f"{lat},{lon}"
        self.mapview.center_on(lat, lon)

        # Vérifier et supprimer l'ancien marqueur si existant
        if hasattr(self, 'gps_marker') and self.gps_marker:
            self.mapview.remove_marker(self.gps_marker)

        # Créer un nouveau marqueur par défaut sur la position GPS
        self.gps_marker = MapMarkerPopup(lat=lat, lon=lon)
        Clock.schedule_once(lambda dt: self.mapview.add_widget(self.gps_marker), 0.1)
        Clock.schedule_once(self.mapview.do_update, 0.1)



    




if __name__ == "__main__":
        main().run()
