"""
Fichier : items.py
Auteur : base technique (game jam)

Description :
Les objets ramassables : fioles de poison (pour se sacrifier au bon endroit),
clés (pour ouvrir les portes) et torches (à planter pour éclairer durablement).

Un objet existe sous deux formes :
  - `Item`  : la donnée pure (type + propriétés), ce qui voyage dans l'inventaire
              et ce qui reste sur un cadavre ;
  - `ItemSprite` : la représentation posée au sol dans le labyrinthe.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import arcade

from src import constants as C
from src.entities.textures import centered_box, load_single

ITEM_TEXTURES = {
    C.ITEM_KEY: "item_key.png",
    C.ITEM_VIAL: "item_vial.png",
    C.ITEM_TORCH: "item_torch_unlit.png",
    C.ITEM_SHIELD: "item_shield.png",
}


@dataclass
class Item:
    """Donnée d'un objet : c'est elle qui circule joueur <-> cadavre <-> sol."""

    type: str
    properties: dict[str, Any] = field(default_factory=dict)

    @property
    def label(self) -> str:
        """Nom court, pour une case d'inventaire ou un titre."""
        return C.ITEM_LABELS.get(self.type, self.type)

    @property
    def phrase(self) -> str:
        """Nom avec son article, pour l'insérer dans une phrase."""
        return C.ITEM_PHRASES.get(self.type, self.label.lower())

    @property
    def key_id(self) -> str | None:
        """Identifiant de serrure, pour les clés uniquement."""
        return self.properties.get("key_id")


class ItemSprite(arcade.Sprite):
    """Objet posé au sol, ramassable avec la touche d'interaction."""

    def __init__(self, item: Item, center_x: float, center_y: float):
        texture_name = ITEM_TEXTURES.get(item.type, "item_key.png")
        super().__init__(
            load_single(texture_name, tuple(centered_box(24, 24))),
            center_x=center_x,
            center_y=center_y,
        )
        self.item = item
        # Léger flottement, pour repérer les objets du coin de l'oeil.
        self._base_y = center_y
        self._time = 0.0

    def update_animation(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        import math

        self._time += delta_time
        self.center_y = self._base_y + math.sin(self._time * 2.4) * 2.0


def make_item_from_map_object(map_object) -> Item:
    """Crée un `Item` à partir d'un objet Tiled (`MapObject`)."""
    return Item(type=map_object.type, properties=dict(map_object.properties))
