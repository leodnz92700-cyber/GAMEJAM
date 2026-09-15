"""
Fichier : tools/import_pack_assets.py
Auteur : base technique (game jam)

Description :
Importe les sprites du pack "Dungeons & Pixels" (dossier `map/dungeonsAndPixels/`)
vers `assets/sprites/` et `assets/maps/`, sous les noms attendus par le jeu.

    python tools/import_pack_assets.py

Le jeu ne lit JAMAIS directement le dossier du pack : il ne connaît que
`assets/`. Ce script est donc le seul endroit à modifier si vous changez de pack
graphique ou si vous voulez utiliser un autre personnage.

Ce qui est importé :
  - le tileset du donjon (+ son .tsx) pour Tiled ;
  - les bandes d'animation du héros (3 directions, idle et course) ;
  - le fantôme, qui sert de créature ;
  - torche, piège, plaque de pression (animés) ;
  - portes de face et de profil, ouvertes et fermées ;
  - fiole, clé, ossements (le cadavre), escalier de sortie.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "map" / "dungeonsAndPixels"
SPRITES = ROOT / "assets" / "sprites"
MAPS = ROOT / "assets" / "maps"

# Copies directes : (source dans le pack, nom de destination)
DIRECT_COPIES = [
    ("Characters/Hero_Warrior/Strips/Idle/down_strip.png", "player_idle_down.png"),
    ("Characters/Hero_Warrior/Strips/Idle/side_strip.png", "player_idle_side.png"),
    ("Characters/Hero_Warrior/Strips/Idle/up_strip.png", "player_idle_up.png"),
    ("Characters/Hero_Warrior/Strips/Run/down_strip.png", "player_run_down.png"),
    ("Characters/Hero_Warrior/Strips/Run/side_strip.png", "player_run_side.png"),
    ("Characters/Hero_Warrior/Strips/Run/up_strip.png", "player_run_up.png"),
    ("Enemies/Ghost/Strips/idle_strip.png", "monster_idle.png"),
    ("Enemies/Ghost/Strips/move_strip.png", "monster_move.png"),
    ("Props/Animated/torch_strip.png", "torch_strip.png"),
    ("Props/Animated/trap1_strip.png", "trap_spike_strip.png"),
    ("Props/Animated/pressure_plate_strip.png", "plate_strip.png"),
    ("Props/Static/Front_Door_Closed.png", "door_front_closed.png"),
    ("Props/Static/Front_Door_Open.png", "door_front_open.png"),
    ("Props/Static/Side_Door_Closed.png", "door_side_closed.png"),
    ("Props/Static/Side_Door_Open.png", "door_side_open.png"),
    ("Props/Static/bones1.png", "corpse.png"),
    ("Props/Static/bones2.png", "corpse_alt.png"),
    ("Items/Static/health_potion.png", "item_vial.png"),
    ("Items/Static/golden_key.png", "item_key.png"),
    ("Enemies/Skeleton warrior/Strips/Idle/down_strip.png", "npc_idle.png"),
]

TILE = 32
TILESET_COLUMNS = 12


def tile_image(tileset: Image.Image, tile_id: int) -> Image.Image:
    """Découpe une tuile du tileset du donjon par son identifiant Tiled."""
    col = tile_id % TILESET_COLUMNS
    row = tile_id // TILESET_COLUMNS
    return tileset.crop((col * TILE, row * TILE, (col + 1) * TILE, (row + 1) * TILE))


def import_tileset() -> None:
    """Copie le tileset du donjon dans assets/maps et génère son .tsx pour Tiled."""
    source = PACK / "Tilesets" / "Tileset_Dungeon.png"
    shutil.copy(source, MAPS / "Tileset_Dungeon.png")
    image = Image.open(source)
    columns = image.width // TILE
    count = columns * (image.height // TILE)
    (MAPS / "Tileset_Dungeon.tsx").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<tileset version="1.10" tiledversion="1.11.0" name="Tileset_Dungeon" '
        f'tilewidth="{TILE}" tileheight="{TILE}" tilecount="{count}" columns="{columns}">\n'
        f' <image source="Tileset_Dungeon.png" width="{image.width}" height="{image.height}"/>\n'
        "</tileset>\n",
        encoding="utf-8",
    )


def import_exit() -> None:
    """
    Construit le sprite de sortie : l'escalier du tileset (deux tuiles empilées).

    Les tuiles 42 et 54 forment un escalier vers le haut, c'est exactement la
    sortie vers l'etage suivant decrite dans le pitch.
    """
    tileset = Image.open(PACK / "Tilesets" / "Tileset_Dungeon.png").convert("RGBA")
    stairs = Image.new("RGBA", (TILE, TILE * 2), (0, 0, 0, 0))
    stairs.paste(tile_image(tileset, 42), (0, 0))
    stairs.paste(tile_image(tileset, 54), (0, TILE))
    stairs.save(SPRITES / "exit.png")

    # Tuile percee d'une grille : sert d'emetteur pour le piege a flechettes.
    tile_image(tileset, 4).save(SPRITES / "trap_dart.png")


def import_torch_item() -> None:
    """Icône d'inventaire de la torche : la première image de l'animation."""
    strip = Image.open(PACK / "Props/Animated/torch_strip.png").convert("RGBA")
    strip.crop((0, 0, TILE, TILE)).save(SPRITES / "item_torch.png")


def main() -> None:
    if not PACK.exists():
        raise SystemExit(
            f"Pack introuvable : {PACK}\n"
            "Placez le dossier 'dungeonsAndPixels' dans 'map/' a la racine du projet."
        )
    SPRITES.mkdir(parents=True, exist_ok=True)
    MAPS.mkdir(parents=True, exist_ok=True)

    missing = []
    for source, destination in DIRECT_COPIES:
        path = PACK / source
        if not path.exists():
            missing.append(source)
            continue
        shutil.copy(path, SPRITES / destination)

    import_tileset()
    import_exit()
    import_torch_item()

    if missing:
        print("ATTENTION, fichiers absents du pack :")
        for source in missing:
            print("  -", source)
    print(f"Sprites importes dans {SPRITES}")


if __name__ == "__main__":
    main()
