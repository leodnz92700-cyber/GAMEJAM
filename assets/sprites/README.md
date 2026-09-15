# assets/sprites/

Toutes les images du jeu.

**Ces fichiers sont importés automatiquement**, ne les modifiez pas à la main :

```bash
python tools/import_pack_assets.py
```

Le script prend les sprites du pack **Dungeons & Pixels** (`map/dungeonsAndPixels/`)
et les dépose ici sous les noms attendus par le code. Le jeu ne lit jamais le
dossier du pack directement : pour changer de personnage ou de pack graphique,
modifiez `tools/import_pack_assets.py` et rien d'autre.

## Ce que le code attend

| Fichier                              | Format             | Utilisé par                  |
|--------------------------------------|--------------------|------------------------------|
| `player_idle_{down,side,up}.png`     | bande de 32x48     | `entities/player.py`         |
| `player_run_{down,side,up}.png`      | bande de 32x48     | `entities/player.py`         |
| `monster_idle.png`, `monster_move.png` | bande de 32x48   | `entities/monster.py`        |
| `torch_strip.png`                    | bande de 32x32     | `environment/torch.py`       |
| `trap_spike_strip.png`               | bande de 32x32     | `environment/trap.py`        |
| `plate_strip.png`                    | bande de 32x32     | `environment/pressure_plate.py` |
| `door_front_{closed,open}.png`       | 32x48              | `environment/door.py`        |
| `door_side_{closed,open}.png`        | 64x64              | `environment/door.py`        |
| `corpse.png`                         | 32x32              | `entities/corpse.py`         |
| `item_{key,vial,torch}.png`          | 32x32              | `entities/items.py`          |
| `exit.png`                           | 32x64 (escalier)   | `mechanics/level_manager.py` |
| `trap_dart.png`                      | 32x32              | `environment/trap.py`        |
| `dart.png`, `light_gradient.png`     | générés            | `tools/gen_placeholder_assets.py` |

La marche vers la gauche n'existe pas dans le pack : le code retourne la bande
"profil" (voir `entities/textures.py`).

## Attention aux boîtes de collision

Les sprites de personnages font 32x48 alors que les couloirs les plus étroits
font 32 px. Leur boîte de collision est donc un petit rectangle **centré**
(`centered_box`), pas la taille de l'image. Si vous changez de sprites, gardez
ce principe et relancez `python tools/walk_test.py`.

Le dessin est en plus remonté de `PLAYER_ART_LIFT` pixels au-dessus du point de
collision (`lift_art` dans `entities/textures.py`) : sans ça, les pieds du
personnage s'enfoncent dans le mur du bas quand il avance vers le sud. Réglez
cette valeur si votre nouveau personnage n'a pas la même hauteur.
