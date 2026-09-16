# Dossier `src/views/`

Contient les différents écrans du jeu, gérés par le système de vues (Views)
d'Arcade.

- **game_view.py** : L'écran principal du jeu (le labyrinthe plongé dans le noir).
- **main_menu.py** : Écran d'accueil — logo, lore, choix du mode de jeu, tableau
  des scores local et musique d'ambiance. Toute sa mise en page tient dans les
  constantes de grille en haut du fichier : deux colonnes qui commencent et
  finissent exactement aux mêmes ordonnées.
- **end_screen.py** : la mise en page COMMUNE aux deux écrans de fin. Les deux
  disent la même chose — voici ta partie, voici tes morts — et seuls le titre,
  sa couleur et la phrase de verdict changent. C'est ici qu'on touche à la
  disposition, pas dans les deux vues.
- **victory_view.py** : Écran de victoire (la sortie est atteinte). Choisit le
  titre et la phrase de verdict, puis délègue à `end_screen`.
- **game_over_view.py** : Écran de défaite (dévoré, ou limite du mode de jeu
  atteinte). Même principe.

Le jeu ne contient **qu'un seul niveau** : il n'y a plus d'écran de sélection
d'étage.
