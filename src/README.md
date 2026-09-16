# Dossier `src/`

Code source principal du jeu.

Ce dossier contient toute la logique de *Labyrinth of Shadow*. Il est divisé en
sous-dossiers spécifiques pour séparer les entités, l'environnement, les
mécaniques de jeu (lumière, gestion de la mort) et les vues (menus, écrans).

- **constants.py** : toutes les constantes du jeu (taille des tuiles, rayons
  d'éclairage, temps avant que la créature soit lâchée, vitesses, couleurs,
  modes de jeu, liste des niveaux). C'est le fichier d'équilibrage : aucune
  valeur de gameplay ne doit être écrite en dur ailleurs.

## Ordre de lecture conseillé

1. `views/game_view.py` : la boucle de jeu, qui orchestre tout le reste.
2. `mechanics/death_manager.py` : la règle centrale (mort choisie vs subie).
3. `mechanics/level_manager.py` : construction d'un étage et découpage en zones.
4. `mechanics/lighting_engine.py` : l'obscurité et les halos.
