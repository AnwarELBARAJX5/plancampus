from DatabaseManager import *
import sqlite3

generer_salles_batiment(15, [0,0, 8, 2, 13, 5],[0,1,  1, 12, 1,9])
generer_salles_batiment(5, [13,0, 13, 6],[1, 0, 1, 5])
generer_salles_batiment(7, [5,0, 7, 2],[1, 0, 0, 0]) #salle 7-05? manquante
generer_salles_batiment(6, [5],[0])
generer_salles_batiment(3, [2],[1])#salle 3-05? manquante
generer_salles_batiment(1, [],[])
generer_salles_batiment(8, [2],[1])
generer_salles_batiment(9, [1],[2]) #salle 9-05? manquante
generer_salles_batiment(14,[10,28,13],[1,0,0])
generer_salles_batiment(2,[],[])
generer_salles_batiment(13,[],[])
generer_salles_batiment(16,[],[])
generer_salles_batiment(17,[],[])

ajouter_salles(7,["7-051","7-050"])
ajouter_salles(6,["Bibliotèque Universitaire"])
ajouter_salles(2,["Grand Amphi"])
ajouter_salles(3,["3-050","3-051","3-052"])
ajouter_salles(5,["Amphi Fabry","Amphi Perès","Amphi Marion","Amphi Lavoisier"])
ajouter_salles(8,["Amphi Sciences Naturelles"])
ajouter_salles(9,["Amphi Charve","9-051","9-050"])
ajouter_salles(7,["Amphi Massiani"])
ajouter_salles(13,["Gymnase"])
ajouter_salles(16,["Restaurant Universitaire"])
ajouter_salles(17,["Cité Universitaire"])
