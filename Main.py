from kivy.config import Config

# Définir la taille pour un téléphone (ex : 400x800 pixels)
Config.set('graphics', 'width', '400')   
Config.set('graphics', 'height', '600')  

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.mapview.geojson import GeoJsonMapLayer
from kivy.clock import Clock
import os

KV = """
BoxLayout:
    orientation: 'vertical'
    
    MDTopAppBar:
        title: 'Carte Kivy'
        size_hint_y: 0.1  # Ajuste la hauteur de la barre
    
    MapView:
        id: mapview
        lat: 43.305446
        lon: 5.377284
        zoom: 18
        size_hint: 1, 1
"""

class Main(MDApp):
    def build(self):
        screen = Builder.load_string(KV)
        self.mapview = screen.ids.mapview
        self.geojson_layers = []  # Stocker les couches GeoJSON

        # Ajout d'un marqueur sur la carte
        marker = MapMarker(lat=43.305446, lon=5.377284)
        self.mapview.add_widget(marker)

        # Charger les fichiers GeoJSON
        directory_path = r"C:\Users\anwar\Documents\GitHub\plancampus\batgeojson"
        files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.geojson')]
        self.load_geojson_layers(files)

        # Lancer l’animation de clignotement
        Clock.schedule_interval(self.toggle_opacity, 0.5)

        return screen

    def load_geojson_layers(self, geojson_files):
        """Ajoute plusieurs fichiers GeoJSON à la carte et les stocke pour l'animation."""
        for geojson_file in geojson_files:
            if os.path.exists(geojson_file):
                geojson_layer = GeoJsonMapLayer(source=geojson_file)
                geojson_layer.opacity = 1  # Initialiser à 100% de visibilité
                self.mapview.add_widget(geojson_layer)
                self.geojson_layers.append(geojson_layer)  # Stocker pour animation
            else:
                print(f"⚠️ Erreur : {geojson_file} introuvable.")

    def toggle_opacity(self, dt):
        """Alterner l’opacité entre 0 et 1 pour chaque bâtiment GeoJSON."""
        for layer in self.geojson_layers:
            layer.opacity = 0 if layer.opacity == 1 else 1

if __name__ == "__main__":
    Main().run()
