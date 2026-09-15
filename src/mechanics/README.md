# Dossier `src/mechanics/`

Contient les systèmes et moteurs qui gèrent les règles du jeu.

- **death_manager.py** : Gère la mécanique principale du jeu : la mort volontaire (laisse un cadavre lumineux avec inventaire) VS la mort par la bête (cadavre dévoré, perte des objets).
- **interaction_manager.py** : Gère l'interaction entre le joueur, les objets, et l'environnement.
- **inventory_system.py** : Gère l'inventaire limité du joueur et la récupération d'objets sur les anciennes dépouilles.
- **level_manager.py** : Gère la transition entre chaque étage de la tour.
- **lighting_engine.py** : Le moteur de lumière. L'obscurité est centrale dans le pitch. Gère le vacillement des torches et la faible lueur émise par les cadavres.
- **monster_manager.py** : Gère la menace invisible. Déclenche les signaux sonores et visuels (torches qui vacillent, pas, grognements) pour forcer le joueur à choisir entre fuir ou se suicider.
- **score_manager.py** : Enregistre le temps, le nombre de morts et autres stats pour l'écran de fin.
