# assets/maps/

Les niveaux, au format **Tiled** (`.tmx`), un fichier par étage de la tour, plus
le tileset du pack Dungeons & Pixels (`Tileset_Dungeon.png` + `.tsx`, importés
par `tools/import_pack_assets.py`).

Les fichiers actuels (`level_test.tmx`, `level_01.tmx`, `level_02.tmx`) sont
générés par `tools/gen_placeholder_maps.py`. Ouvrez-les dans Tiled et redessinez
par-dessus : le jeu n'a pas besoin d'être modifié.
Ne relancez plus le générateur une fois vos cartes dessinées, il écrase tout.

## Structure d'un niveau

- 4 zones (2x2). **Une zone = un écran** : la caméra est fixe et saute d'une
  zone à l'autre quand le joueur franchit une frontière.
- Les frontières de zone doivent être des **murs pleins**, percés uniquement là
  où l'on veut un passage. Partout ailleurs, le joueur doit trouver un mur.
- Les couloirs font **1 ou 2 tuiles** de large. Ceux d'une seule tuile sont les
  plus angoissants : gardez-en. Les salles (4 par zone) servent de respiration
  et d'endroit où poser des objets.

## Convention attendue par le chargeur (`src/mechanics/map_loader.py`)

**Calques de tuiles**

| Calque  | Rôle                                                    |
|---------|---------------------------------------------------------|
| `Floor` | le sol, purement décoratif                              |
| `Walls` | les murs : tout ce qui est dessiné ici bloque le joueur   |

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
| `Traps`           | `spike`           | cyclique une fois découvert (voir plus bas)            |
| `Traps`           | `dart`            | `direction` (up/down/left/right), `interval`, `speed` |
| `NPCs`            | `npc`             | `lines` (répliques séparées par `\|`), `wants_item`    |

`passage` vaut `horizontal` (le joueur traverse la porte en allant à gauche ou à
droite, sprite de profil) ou `vertical` (il la traverse en montant ou en
descendant, sprite de face). **Une porte doit être posée sur un couloir d'une
seule tuile**, sinon on peut la contourner.

**Propriétés de la carte** : `zone_cols` et `zone_rows` (en tuiles) définissent
le découpage en écrans — 40 x 20 par défaut, soit exactement un écran. Gardez
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
- **Les pièges à pointes barrent le couloir** : ils sont invisibles jusqu'à leur
  première victime, puis battent en continu (pointes sorties ~1,1 s, rentrées
  ~1,9 s, réglable dans `constants.py`). On peut donc les franchir en observant
  leur rythme, et s'y jeter volontairement pour laisser un cadavre au bon
  endroit. Ne les rendez jamais mortels en permanence : dans un couloir d'une
  tuile, c'est un cul-de-sac définitif.
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
