import folium
import os
import geojson

# Définir la localisation du campus Saint-Charles
loc = (43.305446, 5.377284)

# Créer la carte
map1 = folium.Map(location=loc, width="75%", zoom_start=18)


# Chemin du répertoire contenant les fichiers GeoJSON
directory_path = r"C:\Users\anwar\Desktop\projetinfo\batgeojson"
files = geojson.get_geojson_files(directory_path)

print("Fichiers trouvés :", files)

# Ajouter chaque fichier GeoJSON à la carte
for file in files:
    path = os.path.join(directory_path, file)  # Construit le chemin correct
    try:
        folium.GeoJson(path, name=file).add_to(map1)  # Utilise `path` au lieu de `file`
        print(f"Ajouté : {path}")
    except Exception as e:
        print(f"Erreur avec {path}: {e}")

# Sauvegarder la carte
output_path = r"C:\Users\anwar\Desktop\projetinfo\map2.html"
map1.save(output_path)
print(f"La carte a été sauvegardée ici : {output_path}")
