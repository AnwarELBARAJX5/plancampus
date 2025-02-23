import requests
import json
import polyline





def get_valhalla_route(start, end, filename="itineraire_valhalla.geojson"):
    """
    Récupère un itinéraire pédestre entre deux points et le sauvegarde en GeoJSON.

    Arguments :
    - start : [longitude, latitude] du point de départ
    - end   : [longitude, latitude] du point d'arrivée
    - filename : Nom du fichier de sortie (par défaut "itineraire_valhalla.geojson")
    
    Retourne :
    - Le chemin sous forme de liste de coordonnées [(lon, lat), (lon, lat), ...]
    - Sauvegarde le fichier GeoJSON
    """

    # 📌 API Valhalla
    url = "https://valhalla1.openstreetmap.de/route"

    # 📌 Construire la requête JSON
    data = {
        "locations": [
            {"lat": start[1], "lon": start[0]},  # ⚠ LATITUDE en premier
            {"lat": end[1], "lon": end[0]}
        ],
        "costing": "pedestrian",  # Mode piéton
        "directions_options": {"units": "kilometers"}
    }

    # 📌 Envoyer la requête
    response = requests.post(url, json=data)

    if response.status_code == 200:
        route = response.json()
        print("✅ Itinéraire trouvé !")

        # 📌 Extraire et décoder la polyline
        encoded_polyline = route["trip"]["legs"][0]["shape"]
        coordinates = polyline.decode(encoded_polyline)

        # 📌 Correction des coordonnées (inverse lat/lon)
        corrected_coordinates = [[lon/10, lat/10] for lat, lon in coordinates]

        # 📌 Construire le fichier GeoJSON
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": corrected_coordinates
                    },
                    "properties": {"name": "Itinéraire Valhalla"}
                }
            ]
        }

        # 📌 Sauvegarde du fichier GeoJSON
        with open(filename, "w") as f:
            json.dump(geojson_data, f)

        print(f"✅ Fichier '{filename}' créé avec succès !")

        return corrected_coordinates  # Retourne la liste des coordonnées

    else:
        print("❌ Erreur API :", response.text)
        return None  # En cas d'erreur, retourne None

# 📌 Exemple d'utilisation
start_point = [5.377899, 43.304687]  # 📍 Campus Saint-Charles
end_point = [5.379358, 43.306450]    # 📍 Destination

# 📌 Lancer la fonction
route_coordinates = get_valhalla_route(start_point, end_point)

# 📌 Vérifier le résultat
if route_coordinates:
    print("\n🗺️ Coordonnées du chemin :", route_coordinates[:5], "...")  # Afficher les 5 premières coordonnées
