# assets/maps/

Fichiers de niveaux, un par étage/manche de la tour.

- Format Tiled (`.tmx`) si vous utilisez l'éditeur Tiled, ou une
  matrice/grille en JSON maison si vous préférez tout coder à la
  main (plus rapide à faire évoluer pour une Game Jam si personne
  ne connaît Tiled).
- Chaque fichier doit encoder au minimum : les murs, le point de
  départ, le point d'arrivée, l'emplacement des clés et des portes
  correspondantes, les plaques de pression, et l'emplacement de la
  porte spéciale liée au timer caché (même si elle reste fermée au
  chargement).
- Nommer par numéro d'étage clair (`level_01.json`, `level_02.json`)
  pour que `mechanics/map_parser.py` puisse les charger dans l'ordre
  sans logique spéciale.

Gardez une carte "test" simple et courte (`level_test.json`) séparée
des vraies manches, pratique pour itérer vite sur une mécanique sans
retraverser tout un niveau à chaque fois.
