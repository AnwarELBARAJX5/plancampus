import requests
import json

# 📌 Ta clé API OpenRouteService (remplace-la par la tienne)
ORS_API_KEY = "5b3ce3597851110001cf624883181b06add74d679245db2128ba978b"


# 📌 Coordonnées du départ et de l'arrivée (longitude, latitude)
start = [5.3795,43.3059]  # Campus Saint-Charles
end = [	5.3794,43.3065]    # Destination

# 📌 URL de l'API ORS pour les itinéraires piétons
url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"

# 📌 Construire la requête POST
headers = {
    "Authorization": ORS_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "coordinates": [start, end],
    "format": "geojson",
    "preference": "fastest"
    
}

# 📌 Envoyer la requête POST
response = requests.post(url, headers=headers, json=payload)

# 📌 Vérifier la réponse
if response.status_code == 200:
    route = response.json()
    print("✅ Itinéraire trouvé !")

    # 📌 Sauvegarder l'itinéraire en GeoJSON
    with open("itineraire.geojson", "w") as f:
        json.dump(route, f)

    print("✅ Fichier 'itineraire.geojson' créé avec succès !")

else:
    print("❌ Erreur lors du calcul de l’itinéraire :", response.text)


import asyncio
from winsdk.windows.devices.geolocation import Geolocator, PositionStatus

async def get_precise_location():
    locator = Geolocator()

    if locator.location_status in [PositionStatus.NOT_AVAILABLE, PositionStatus.DISABLED]:
        print("⚠️ Localisation désactivée ou non disponible.")
        return None

    pos = await locator.get_geoposition_async()  # ← await nécessaire ici
    coord = pos.coordinate
    lat = coord.point.position.latitude
    lon = coord.point.position.longitude
    accuracy = coord.accuracy
    print(f"📍 Latitude : {lat}, Longitude : {lon}, Précision : {accuracy} m")
    return lat, lon

# Exécution de la fonction async dans un contexte normal :
if __name__ == "__main__":
    asyncio.run(get_precise_location())