import os

def get_geojson_files(directory):
    """Récupère tous les fichiers .geojson dans un répertoire donné."""
    if not os.path.exists(directory):
        print(f"Le répertoire {directory} n'existe pas.")
        return []
    if not os.path.isdir(directory):
        print(f"{directory} n'est pas un répertoire valide.")
        return []

    return [file for file in os.listdir(directory) if file.endswith(".geojson")]
def path(directory_path):
    liste=[]
    files=get_geojson_files(directory_path)
    for file in files:
        path = os.path.join(directory_path, file)  # Construit le chemin correct
        liste.append(path)
    try:
        print(f"Ajouté : {path}")
    except Exception as e:
        print(f"Erreur avec {path}: {e}")
    return liste

def path_suffixe(str,path):
    position = path.rfind("\\")
    nom_fichier = path[position + 1:]
    if nom_fichier==str:
        return True
    else:
        return False
