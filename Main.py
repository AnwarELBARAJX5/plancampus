from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')


from kivy.lang import Builder
from kivymd.app import MDApp
from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy.clock import Clock
import itineraire as itineraire
import os


# 📌 Fichier KV (Interface utilisateur)
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

        TextInput:
            id: start_location
            hint_text: "Entrer le point de départ (lon, lat)"
            multiline: False
            size_hint_y: None
            height: 40

        TextInput:
            id: end_location
            hint_text: "Entrer la destination (lon, lat)"
            multiline: False
            size_hint_y: None
            height: 40

        Button:
            text: "Trouver l'itinéraire"
            size_hint_y: None
            height: 40
            on_release: app.calculate_route()

        
"""

class Main(MDApp):
    def build(self):
        screen = Builder.load_string(KV)
        self.mapview = screen.ids.mapview
        self.geojson_layers = []  
        self.route_layer = None
        # 📌 Charger les fichiers GeoJSON des bâtiments
        self.load_geojson_layers("batgeojson")

        # 📌 Animation clignotante pour les bâtiments
        Clock.schedule_interval(self.toggle_opacity, 0.5)

        return screen

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

    def calculate_route(self):
        start_text = self.root.ids.start_location.text
        end_text = self.root.ids.end_location.text
        start = [float(coord) for coord in start_text.split(",")]
        end = [float(coord) for coord in end_text.split(",")]
        path = os.path.join(os.getcwd(), "batgeojson")
        filename = os.path.join(path, "itineraire_valhalla.geojson")

        chemin=itineraire.get_valhalla_route(start,end,filename)
     
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
