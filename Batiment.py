class Batiment:
    def __init__(self, numBat, salleParetage, indices_depart=None, nom=""):
        if len(salleParetage) != len(indices_depart):
            raise ValueError("Les listes salleParetage et indices_depart doivent avoir la même longueur.")
        
        self.numBat = numBat
        self.salleParetage = salleParetage
        self.nbetage = len(salleParetage) if salleParetage else 0
        self.listesalle = []
        self.indices_depart = indices_depart if indices_depart else [1] * len(salleParetage)
        self.nom = nom if nom else f"Bâtiment {numBat}"

    def generationlistesalle(self):
        """Génère une liste de salles avec le format 'batiment-etage_salle'."""
        self.listesalle = []
        
        for etage, (nb_salles, indice_depart) in enumerate(zip(self.salleParetage, self.indices_depart), start=0):
            if nb_salles > 0:
                for num_salle in range(indice_depart, indice_depart + nb_salles):
                    self.listesalle.append(f"{self.numBat}-{etage}{num_salle:02}")

    def afficher_salles(self):
        """Affiche la liste des salles ou un message si le bâtiment n'a pas de salles."""
        print(f"\n{self.nom}:")
        if not self.listesalle:
            print("→ Ce bâtiment n'a pas de salles.")
        else:
            for salle in self.listesalle:
                print(salle)


# Fonction externe pour générer et afficher les salles d'un bâtiment
def generer_salles_batiment(numBat, salleParetage, indices_depart=None):
    # Créer une instance du bâtiment
    batiment = Batiment(numBat, salleParetage, indices_depart)
    
    # Générer les salles
    batiment.generationlistesalle()
    
    # Afficher les salles
    batiment.afficher_salles()


batiment15 = Batiment(15, [0, 8, 2, 13, 5], [1,  1, 12, 1,9])  # Indices de départ pour chaque étage
batiment15.generationlistesalle()  # Génère les salles
batiment15.afficher_salles()