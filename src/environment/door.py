"""
Fichier : door.py
Auteur : base technique (game jam)

Description :
Les portes du labyrinthe. Deux variantes de fonctionnement :
  - `door_key`   : verrouillée, s'ouvre définitivement avec la bonne clé ;
  - `door_plate` : reliée à une plaque de pression, ouverte tant que la plaque
                   est enfoncée (par le joueur ou, mieux, par un cadavre).

Et deux variantes d'aspect, selon le sens du passage qu'elles bouchent : porte
de face (couloir vertical) ou porte de profil (couloir horizontal). Les images
du pack sont plus grandes que le passage lui-même (une porte de profil fait
64x64 pour une tuile de passage) : on leur donne donc une boîte de collision
réduite à la tuile, sinon la porte bloquerait les murs alentour.

Une porte fermée bloque physiquement le joueur : elle vit dans une liste de
collisions séparée (`door_blocker_list`) que le moteur physique consulte. Ouvrir
une porte revient simplement à l'en retirer.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.textures import load_single

# (texture fermée, texture ouverte, décalage vertical du sprite par rapport à
# la tuile de passage). Les portes de face sont hautes de 48 px : on les remonte
# de 8 px pour que leur base coïncide avec la tuile.
DOOR_ART = {
    "vertical": ("door_front_closed.png", "door_front_open.png", 8.0),
    "horizontal": ("door_side_closed.png", "door_side_open.png", 0.0),
}


def _passage_hit_box(texture_width: int, texture_height: int,
                     offset_y: float) -> tuple:
    """Boîte de collision réduite à la tuile de passage, sous le sprite."""
    half = C.TILE_SIZE / 2
    center_y = -offset_y
    return (
        (-half, center_y - half),
        (half, center_y - half),
        (half, center_y + half),
        (-half, center_y + half),
    )


class Door(arcade.Sprite):
    """Porte pilotée par une clé ou par une plaque de pression."""

    def __init__(self, center_x: float, center_y: float, door_id: str,
                 key_id: str | None = None, plate_id: str | None = None,
                 passage: str = "vertical"):
        closed_name, open_name, offset_y = DOOR_ART.get(passage, DOOR_ART["vertical"])
        probe = load_single(closed_name)
        hit_box = _passage_hit_box(probe.width, probe.height, offset_y)

        self.texture_closed = load_single(closed_name, hit_box)
        self.texture_open = load_single(open_name, hit_box)
        super().__init__(
            self.texture_closed,
            center_x=center_x,
            center_y=center_y + offset_y,
        )

        self.door_id = door_id
        self.key_id = key_id
        self.plate_id = plate_id
        self.passage = passage
        self.is_open = False
        # Une porte à clé reste ouverte une fois déverrouillée ; une porte à
        # plaque se referme dès que la plaque se relève.
        self.permanent = key_id is not None

    @property
    def needs_key(self) -> bool:
        return self.key_id is not None

    def open(self) -> None:
        self.is_open = True
        self.texture = self.texture_open

    def close(self) -> None:
        if self.permanent:
            return
        self.is_open = False
        self.texture = self.texture_closed


def make_door_from_map_object(map_object, loaded_map=None) -> Door:
    """Construit la bonne variante de porte à partir d'un objet Tiled."""
    properties = map_object.properties
    door_id = str(properties.get("door_id") or properties.get("groupe") or f"door_{int(map_object.center_x)}")
    is_plate_door = map_object.type == "door_plate" or "plate_id" in properties or "groupe" in properties
    
    passage = str(properties.get("passage", "vertical"))
    if "passage" not in properties:
        if loaded_map:
            col = int(map_object.center_x // 32)
            row = int(map_object.center_y // 32)
            wall_above = row < loaded_map.height_tiles - 1 and not loaded_map.walkable[row+1][col]
            wall_below = row > 0 and not loaded_map.walkable[row-1][col]
            wall_left = col > 0 and not loaded_map.walkable[row][col-1]
            wall_right = col < loaded_map.width_tiles - 1 and not loaded_map.walkable[row][col+1]
            if wall_above or wall_below:
                passage = "horizontal"
            elif wall_left or wall_right:
                passage = "vertical"
            elif getattr(map_object, "rotation", 0.0) and abs(map_object.rotation) in (90, 270):
                passage = "horizontal"
        
    return Door(
        center_x=map_object.center_x,
        center_y=map_object.center_y,
        door_id=door_id,
        key_id=None if is_plate_door else str(properties.get("key_id", "key_1")),
        plate_id=door_id if is_plate_door else None,
        passage=passage,
    )
