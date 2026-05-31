Documentation:

mbtiles : 
Lancer ubuntu
Lancer la commande "tippecanoe -0 monfichier.mbtiles maligne1.geojson maligne2.geojson maligne3.geojson
Le fichier résultant comportera autant d'objets paramètrables que de geojson dans SDVFR Next

main.py:
Demande à l'utilisateur de choisir une carte 
    - si not OK :
        - Quitte le programme
    - si Ok :
        - Charge les menus
        - Initialise les bases de données SQLite si non presentes

A la fermeture demande pour la sauvegarde du travail :
    - Oui : Les bases de données ne sont pas effacées + Fermeture
    - Non : Les bases de données sont effacées + Fermeture
