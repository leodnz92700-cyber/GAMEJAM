# assets/maps/

Les niveaux, au format **Tiled** (`.tmx`), plus le tileset du pack Dungeons &
Pixels (`Tileset_Dungeon.png` + `.tsx`, importés par
`tools/import_pack_assets.py`).

Le jeu ne joue qu'**un seul niveau**, `level_01.tmx` (`C.LEVEL_NAME`) :
atteindre sa sortie gagne la partie. `level_test.tmx` n'est là que pour itérer
vite pendant le développement, il n'est jamais joué par une vraie partie.

Les fichiers actuels (`level_test.tmx`, `level_01.tmx`) sont
générés par `tools/gen_placeholder_maps.py`. Ouvrez-les dans Tiled et redessinez
par-dessus : le jeu n'a pas besoin d'être modifié.
Ne relancez plus le générateur une fois vos cartes dessinées, il écrase tout.

## Structure d'un niveau

- 4 zones (2x2), soit une carte de 80 x 44 tuiles. **Une zone = un écran** : la
  caméra est fixe et saute d'une zone à l'autre quand le joueur franchit une
  frontière. Ces dimensions viennent de `src/constants.py` (`ZONE_COLS`,
  `ZONE_ROWS`, `ZONES_X`, `ZONES_Y`) — si vous les changez, régénérez ou
  redimensionnez les cartes en conséquence.
- Les frontières de zone doivent être des **murs pleins**, percés uniquement là
  où l'on veut un passage. Partout ailleurs, le joueur doit trouver un mur.
- Les couloirs font **1 ou 2 tuiles** de large. Ceux d'une seule tuile sont les
  plus angoissants : gardez-en. Les salles (4 par zone) servent de respiration
  et d'endroit où poser des objets.

## Convention attendue par le chargeur (`src/mechanics/map_loader.py`)

**Calques de tuiles**

| Calque         | Rôle                                                            |
|----------------|-----------------------------------------------------------------|
| `Floor`        | le sol, purement décoratif                                      |
| `Walls`        | les murs : tout ce qui est dessiné ici bloque le joueur           |
| `Shadow_layer` | **optionnel**, décor pur : dessiné juste au-dessus du sol         |
| `Props_layer`  | **optionnel**, décor pur : dessiné juste au-dessus des murs       |

`Shadow_layer` et `Props_layer` ne bloquent jamais le joueur et ne sont lus par
aucune logique de jeu : c'est `map_loader.py` qui les charge (s'ils existent) et
`game_view._draw_world()` qui les dessine, dans le même ordre que Tiled les
empile déjà (ombres sous le décor, props par-dessus les murs). Une carte qui
n'a pas ces calques continue de fonctionner normalement : ils sont chargés en
liste vide si absents.

**Calques d'objets** — c'est la **classe** de l'objet Tiled (champ `Class`, ou
`Type` dans les anciennes versions) qui détermine ce qui est créé. Sauf mention
contraire, un objet occupe **une seule tuile** : pour barrer un couloir de deux
tuiles avec des pièges, posez deux objets côte à côte.

| Calque            | Classe            | Propriétés                                            |
|-------------------|-------------------|-------------------------------------------------------|
| `Spawn`           | `spawn`           | —                                                     |
| `Exit`            | `exit`            | la tuile du bas de l'escalier (le sprite fait 2 tuiles) |
| `Items`           | `key`             | `key_id` : la serrure correspondante                   |
| `Items`           | `vial`            | **une seule par niveau**, à quelques pas du départ      |
| `Items`           | `torch`           | en semer beaucoup (voir plus bas)                      |
| `Doors`           | `door_key`        | `door_id`, `key_id`, `passage`                        |
| `Doors`           | `door_plate`      | `door_id`, `plate_id`, `passage`                      |
| `PressurePlates`  | `pressure_plate`  | `plate_id`, `door_id` (la porte commandée)             |
| `Traps`           | `spike`           | visible et cyclique (voir plus bas)                   |
| `Traps`           | `archer`          | `direction` (up/down/left/right), `interval`, `speed` |
| `NPCs`            | `npc`             | `lines` (répliques séparées par `\|`), `wants_item`    |

`passage` vaut `horizontal` (le joueur traverse la porte en allant à gauche ou à
droite, sprite de profil) ou `vertical` (il la traverse en montant ou en
descendant, sprite de face). **Une porte doit être posée sur un couloir d'une
seule tuile**, sinon on peut la contourner.

**Propriétés de la carte** : `zone_cols` et `zone_rows` (en tuiles) définissent
le découpage en écrans — 40 x 22 par défaut, soit exactement un écran (il n'y a
aucun bandeau d'interface, le jeu occupe toute la fenêtre). Gardez
les dimensions de la carte multiples de ces valeurs.

## Règles de contenu à respecter

- **Une seule fiole**, posée à moins d'une douzaine de tuiles du départ. Elle
  réapparaît toute seule à cet endroit après chaque mort : c'est le seul moyen
  fiable de choisir sa mort, et elle ne doit jamais se stocker.
- **Une clé posée dans la carte est unique et indispensable.** Le jeu la remet
  automatiquement à cet endroit si elle disparaît du niveau (dévorée avec le
  joueur par la créature). Elle n'est PAS remise en place tant qu'elle est sur
  un cadavre : là, elle est toujours dans le niveau, et c'est au joueur d'aller
  la rechercher. Les types concernés sont listés dans `RESPAWNING_ITEM_TYPES`
  (`src/constants.py`) : ajoutez-y tout nouvel objet de quête unique.
- **Beaucoup de torches** (au moins une dizaine, plutôt vingt) réparties le long
  du chemin principal : le joueur doit pouvoir, vie après vie, éclairer tout son
  trajet. Il n'en porte que deux à la fois.
- **Les pièges à pointes barrent le couloir** : ils sont visibles en permanence
  et battent en continu (pointes sorties ~1,1 s, rentrées ~1,9 s, réglable dans
  `constants.py`). Le joueur voit le danger et doit l'esquiver en lisant le
  rythme, ou s'y jeter volontairement pour laisser un cadavre au bon endroit.
  Ne les rendez jamais mortels en permanence : dans un couloir d'une tuile,
  c'est un cul-de-sac définitif.
- **La plaque de pression se pose juste avant sa porte**, dans le couloir qui y
  mène : le joueur doit voir la porte s'ouvrir quand il marche dessus, et se
  refermer quand il avance. C'est ce qui lui fait comprendre qu'il doit mourir
  dessus.

## Vérifier une carte

Après chaque modification dans Tiled :

```bash
python tools/check_levels.py level_01.tmx
python tools/walk_test.py level_01.tmx
```

`check_levels` vérifie la cohérence logique (sortie atteignable, clé pas
enfermée derrière sa propre porte, fiole unique et proche du départ, assez de
torches, durée de parcours). `walk_test` fait réellement traverser le niveau au
joueur avec le moteur de collisions : c'est lui qui détecte un couloir trop
étroit ou un passage bouché.
