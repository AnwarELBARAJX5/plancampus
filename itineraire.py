import requests
import json
import polyline
import os
import sys
sys.path.append(os.path.abspath("batgeojson"))
import test


import requests
import json
import polyline

def get_valhalla_route(start, end, filename="itineraire_valhalla.geojson"):
    """
    Récupère un itinéraire pédestre entre deux points via Valhalla, génère un fichier GeoJSON et le corrige.

    Arguments :
    - start : [longitude, latitude] du point de départ
    - end   : [longitude, latitude] du point d'arrivée
    - filename : Nom du fichier de sortie (par défaut "itineraire_valhalla.geojson")
    
    Retourne :
    - Le chemin sous forme de liste de coordonnées [(lon, lat), (lon, lat), ...]
    - Sauvegarde le fichier GeoJSON corrigé
    """

    url = "https://valhalla1.openstreetmap.de/route"

    data = {
        "locations": [
            {"lat": start[1], "lon": start[0]},  
            {"lat": end[1], "lon": end[0]}
        ],
        "costing": "pedestrian",  
        "directions_options": {"units": "kilometers","language": "fr-FR"}
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        route = response.json()
        print("✅ Itinéraire trouvé !")

        # 🔹 Décoder la polyline et corriger les coordonnées
        encoded_polyline = route["trip"]["legs"][0]["shape"]
        coordinates = polyline.decode(encoded_polyline)
        corrected_coordinates = [[lon/10, lat/10] for lat, lon in coordinates]  # 🔄 Correction lat/lon
        directions = [maneuver["instruction"] for leg in route["trip"]["legs"] for maneuver in leg["maneuvers"]]
        total_distance = route["trip"]["summary"]["length"]  # Distance totale en km
        total_duration = int(route["trip"]["summary"]["time"] / 60)  # Temps en minutes
        maneuvers = route["trip"]["legs"][0]["maneuvers"]
        print(total_distance,total_duration,directions)
        # 🔹 Générer GeoJSON
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": corrected_coordinates
                    },
                    "properties": {
                        "name": "Itinéraire Valhalla",
                        "stroke-width": 2,  # 🔧 Fix automatique
                        "stroke": "#FF0000",
                        "language": "fr-FR"
                    }
                }
            ]
        }

        # 🔹 Sauvegarder le fichier GeoJSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, indent=2)

        print(f"✅ Fichier '{filename}' créé et corrigé avec succès !")
        return {
            "geojson": geojson_data,
            "directions": directions,
            "distance": total_distance,
            "duration": total_duration
        }  

    else:
        print("❌ Erreur API :", response.text)
        return None  




# 📌 Exemple d'utilisation
start_point = [5.378129,43.304599]  # 📍 Campus Saint-Charles
end_point = [5.379358,43.306456]    # 📍 Destination

# 📌 Lancer la fonction
route_coordinates = get_valhalla_route(start_point, end_point)

# 📌 Vérifier le résultat
if route_coordinates:
    print(route_coordinates)