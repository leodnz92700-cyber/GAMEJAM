# Dossier `src/mechanics/`

Contient les systèmes et moteurs qui gèrent les règles du jeu.

- **audio_manager.py** : point d'entrée unique du son. Aucun autre module ne
  connaît un nom de fichier audio : ils demandent un nom LOGIQUE (`door_open`,
  `alert_close`) et ce module sait où le trouver. Le son n'est pas décoratif
  ici : il REMPLACE le compte à rebours, c'est lui qui prévient le joueur de
  l'approche de la créature : grognements par palier, puis respiration qui
  s'affole. L'inventaire complet des sons est dans
  `assets/audio/README.md`, leur volume dans `constants.AUDIO_VOLUMES`.
- **death_manager.py** : gère la mécanique principale du jeu : la mort
  volontaire (le corps reste, les affaires tombent au sol autour de lui) VS la
  mort par la bête (rien ne reste, tout est perdu). La mise en scène de chacune
  — chute du héros, ou jumpscare — est déclenchée par `views/game_view.py`.
- **interaction_manager.py** : gère l'interaction entre le joueur, les objets et
  l'environnement (ramasser un objet au sol, ouvrir une porte, planter une
  torche, boire la fiole). Les cadavres ne se fouillent pas : les affaires d'une
  vie précédente sont posées par terre autour du corps.
- **inventory_system.py** : gère l'inventaire limité du joueur et la
  récupération d'objets sur les anciennes dépouilles.
- **level_manager.py** : construit un étage à partir d'une carte Tiled, simule
  son environnement (plaques, portes, projectiles) et gère l'enchaînement des
  étages ainsi que le découpage en zones.
- **lighting_engine.py** : le moteur de lumière. L'obscurité est centrale dans
  le pitch : voile noir percé par un shader, plus une passe de lueur colorée.
  Gère le vacillement des torches et la lueur des cadavres.
- **map_loader.py** : lit un fichier Tiled `.tmx` et le traduit en données
  neutres (listes de sprites, objets, grille de navigation). Change de format de
  carte sans toucher au reste du jeu.
- **monster_manager.py** : gère la menace invisible. Déclenche les signaux
  sonores et visuels (torches qui vacillent, grognement de chaque palier,
  respiration du héros) pour forcer le joueur à choisir
  entre continuer ou se sacrifier, puis lâche la créature.
- **score_manager.py** : enregistre le temps, le nombre de morts et les autres
  statistiques pour l'écran de fin et le tableau des scores local.
