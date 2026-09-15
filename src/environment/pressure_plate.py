"""
Fichier : pressure_plate.py
Auteur : base technique (game jam)

Description :
Les plaques de pression. Elles s'enfoncent sous le poids du joueur... ou d'un
cadavre. C'est l'usage le plus direct du thème : le joueur doit mourir sur la
plaque pour que la porte associée reste ouverte pendant qu'il va ailleurs.

Les plaques sont posées près de la porte qu'elles commandent, pour que le joueur
puisse voir le résultat de son sacrifice.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.textures import centered_box, load_strip


class PressurePlate(arcade.Sprite):
    """Plaque reliée à une porte par son `door_id`."""

    def __init__(self, center_x: float, center_y: float,
                 plate_id: str, door_id: str | None = None):
        self.frames = load_strip(
            "plate_strip.png", C.TILE_SIZE, C.TILE_SIZE, tuple(centered_box(30, 30))
        )
        super().__init__(self.frames[0], center_x=center_x, center_y=center_y)

        self.plate_id = plate_id
        self.door_id = door_id
        self.is_pressed = False
        self.held_by_corpse = False

    def update_pressed(self, player, corpse_list) -> bool:
        """
        Recalcule l'état de la plaque. Renvoie True si l'état vient de changer.

        On regarde les cadavres en premier : une plaque tenue par un cadavre est
        acquise définitivement, alors qu'une plaque tenue par le joueur se
        relâche dès qu'il s'en va — c'est toute la raison d'être de la mécanique.
        """
        self.held_by_corpse = bool(arcade.check_for_collision_with_list(self, corpse_list))
        pressed = self.held_by_corpse
        if not pressed and player is not None and player.is_alive:
            pressed = arcade.check_for_collision(self, player)

        if pressed == self.is_pressed:
            return False

        self.is_pressed = pressed
        self.texture = self.frames[-1] if pressed else self.frames[0]
        return True


def make_plate_from_map_object(map_object) -> PressurePlate:
    """Construit une plaque à partir d'un objet Tiled."""
    properties = map_object.properties
    return PressurePlate(
        center_x=map_object.center_x,
        center_y=map_object.center_y,
        plate_id=str(properties.get("plate_id", f"plate_{int(map_object.center_x)}")),
        door_id=str(properties["door_id"]) if "door_id" in properties else None,
    )
