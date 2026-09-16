# assets/audio/

Tous les sons et musiques du jeu. **Tout ce qui est listé ici est déjà branché
dans le jeu** : déposer un meilleur fichier sous le même nom suffit, il n'y a
pas une ligne de code à toucher.

Le code ne connaît jamais un chemin de fichier : il demande un **nom logique**
(`door_open`, `alert_close`). La correspondance nom logique → fichier est dans
`src/mechanics/audio_manager.py` (`SOUND_FILES`), et le **volume de chaque son**
dans `src/constants.py` (`AUDIO_VOLUMES`). C'est là qu'on règle le mixage, pas
dans le code.

## Le son remplace le compte à rebours

Règle de game design à ne jamais casser : **aucun compte à rebours n'est affiché**
pour la créature. Le joueur n'a que ce que son personnage entend. Trois signaux
portent cette information, et baisser leur volume revient à retirer au joueur sa
seule horloge :

1. **quatre grognements d'alerte**, un par palier d'approche ;
2. **sa respiration**, souffle occasionnel tant que la bête est loin, halètement
   continu à partir du palier « near » ;
3. **la musique de poursuite**, qui démarre quand la créature est proche — donc
   *avant* qu'elle ne soit visible.

C'est aussi pour cela qu'il n'y a **pas de nappe de fond** : le fond sonore du
jeu est le silence, troué de loin en loin par une goutte d'eau ou un
grincement. Une nappe continue noierait les trois signaux ci-dessus.

## Ce qui est branché

| Nom logique | Fichier | Quand il joue |
|---|---|---|
| `footstep` | `player/footstep.wav` | un pas toutes les 0,34 s tant que le joueur se déplace |
| `breathing` | `player/breathing.wav` | au hasard toutes les 18 à 38 s quand tout est calme ; **en boucle** dès le palier « near » |
| `pain` | `player/pain.wav` | à l'instant où les pointes ou une flèche touchent |
| `potion_get` | `items/potion/get.wav` | ramassage de la fiole |
| `potion_use` | `items/potion/use.wav` | `R` : le joueur boit (le son part au moment de la gorgée, pas à la fin de la chute) |
| `key_get` | `items/key/get.wav` | ramassage d'une clé |
| `key_use` | `items/key/use.wav` | ouverture d'une porte à clé, **superposé** à `door_open` |
| `torch_get` | `items/torch/get.wav` | ramassage d'une torche |
| `torch_use` | `items/torch/use.wav` | `F` : torche plantée |
| `pickup` | `pickup.wav` | objets sans son dédié (le bouclier) |
| `door_open` | `misc/doors/open_wooden_door.wav` | porte ouverte, à la clé **ou** par une plaque |
| `door_locked` | `misc/doors/door_locked.wav` | `E` sur une porte verrouillée sans la clé |
| `plate_press` | `misc/plate/pressure_plate.wav` | une plaque s'enfonce (joueur ou cadavre) |
| `plate_release` | `misc/plate/release_pressure_plate.wav` | une plaque se relâche |
| `spike_strike` | `misc/trap/spiketrap_open.wav` | les pointes jaillissent, **une seule fois par cycle**, d'autant plus fort qu'on est près (voir ci-dessous) |
| `arrow_shot` | `misc/trap/arrow_shot.wav` | l'archer décoche, d'autant plus fort qu'on est près (voir ci-dessous) |
| `water_drop` | `ambiance/water_drop.wav` | ambiance aléatoire, toutes les 12 à 35 s |
| `squeak` | `ambiance/squeak.wav` | idem |
| `menu_music` | `ambiance/mainmenu/mainmenu_sound.mp3` | en boucle sur l'accueil **et** sur les écrans de fin |
| `ui_hover` | `menu/hover_button.wav` | la sélection du menu change (clavier ou souris) |
| `ui_click` | `menu/button_click.wav` | validation d'un bouton |
| `alert_far` | `monster/alerts/far_away.wav` | palier 1 — « Quelque chose remue, loin dans la tour. » |
| `alert_near` | `monster/alerts/mi_distance.wav` | palier 2 — « Des griffes raclent la pierre. » |
| `alert_close` | `monster/alerts/near.wav` | palier 3 — « Des pas courent dans le noir. » |
| `alert_released` | `monster/alerts/now.wav` | palier 4 — « Elle est la. » |
| `monster_released` | `monster/final_timer.wav` | **superposé** à `alert_released` : le sursis est fini |
| `monster_chase` | `monster/monster_chase.wav` | en boucle tant que la créature est à moins de 340 px |
| `monster_kill` | `monster/kill_sound.wav` | le jumpscare : le joueur est dévoré |
| `victory` | `misc/victory.wav` | écran de victoire |
| `game_over` | `misc/game_over.wav` | écran de défaite |

Chaque alerte correspond **exactement** au murmure rouge affiché en haut de
l'écran au même instant : le joueur lit et entend la même chose.

## Les bruits de décor s'entendent de loin, et montent à l'approche

Les pointes et les flèches sont les deux seuls sons qui se répètent sans arrêt :
un piège toutes les 3 s, une flèche toutes les 0,3 s, et **tous les pièges de
l'étage battent en phase**. Entendus au même volume depuis tout le niveau, ils
deviennent un vacarme dans lequel le joueur ne distingue plus rien.

Ils sont donc **atténués avec la distance au joueur**, et la montée n'est pas
linéaire : un filet de son très loin, qui grimpe franchement dans les dernières
tuiles. C'est ce qui permet d'entendre qu'on approche d'un piège, dans le noir,
avant de le voir.

| Distance | Coefficient | Volume réel des pointes |
|---:|---:|---:|
| sur le piège | 1,00 | 0,44 |
| 1 tuile | 0,79 | 0,35 |
| 2 tuiles | 0,62 | 0,27 |
| 4 tuiles | 0,34 | 0,15 |
| 6 tuiles | 0,18 | 0,08 |
| 8 tuiles | 0,00 | silence |

Trois réglages dans `src/constants.py`, et ils comptent tous les trois :

- `AUDIO_NEAR_RANGE` (8 tuiles) — à partir d'où on perçoit quelque chose ;
- `AUDIO_NEAR_MIN_VOLUME` (0,12) — le « tout petit peu » qu'on entend à cette
  limite. **Sans ce plancher, le son apparaît à zéro et on a l'impression d'un
  interrupteur** ; il s'éteint lui-même en douceur sur la dernière tuile, sinon
  c'est le plancher qui claque à l'entrée en portée ;
- `AUDIO_NEAR_CURVE` (2,0) — la courbure. À 1,0 la montée est linéaire et le son
  s'entend déjà beaucoup à mi-distance, si bien qu'on ne perçoit plus le
  rapprochement. Monter la valeur rend le lointain plus discret et l'approche
  plus franche.

Deux pièges qui barrent le même couloir ne sonnent qu'**une fois**, au volume du
plus proche : sinon ils sonneraient deux fois plus fort qu'un piège seul.

## Encore des placeholders de synthèse

Ces trois fichiers sont générés en Python par `tools/gen_placeholder_assets.py`,
sous leur **nom définitif**. Déposez le vrai son par-dessus et c'est fini. Le
générateur ne les réécrit jamais s'ils existent déjà, le relancer ne peut donc
pas effacer une vraie livraison.

- `misc/trap/arrow_shot.wav` — **le plus utile à remplacer** : l'archer tire
  trois fois par seconde dans le noir, c'est l'endroit du jeu qui enseigne le
  pitch. Il faut un son très court et sec (0,2 s maximum), sinon il devient un
  bourdonnement continu ;
- `misc/victory.wav` ;
- `misc/game_over.wav`.

## Fichiers qui ne servent plus

Les placeholders historiques de la racine (`ambience_drone.wav`, `growl_far.wav`,
`scratch.wav`, `steps_close.wav`, `heartbeat.wav`, `devoured.wav`,
`death_vial.wav`, `door_open.wav`, `torch_place.wav`, `plate_click.wav`,
`trap_trigger.wav`) sont **remplacés** par les vrais sons et ne sont plus
chargés. Seul `pickup.wav` sert encore, pour les objets sans son dédié. On peut
supprimer les autres une fois qu'on est sûr de ne plus vouloir comparer.

## Contraintes de format

- Le jeu lit du **WAV** et du **MP3**. Le 24 bits passe, le 96 kHz aussi, mais
  ça pèse dix fois plus lourd pour rien : **16 bits / 44,1 kHz** suffit
  largement pour un bruitage.
- **Coupez le silence et la queue de réverbération** de vos prises. Le premier
  `pressure_plate.wav` livré durait 22,9 s pour 6,3 Mo (quatre prises à la
  suite) : il a dû être recoupé à 0,9 s, sans quoi la plaque déclenchait un son
  de 23 s à chaque pas dessus. Un bruitage d'interaction tient en moins d'une
  seconde.
- Les sons qui bouclent (`breathing`, `monster_chase`, `menu_music`) doivent
  boucler **proprement** : pas de blanc ni de claquement aux extrémités.
- `key/get.wav` et `torch/get.wav` sont pour l'instant **le même fichier**
  (octet pour octet) : la clé et la torche sonnent pareil au ramassage.
