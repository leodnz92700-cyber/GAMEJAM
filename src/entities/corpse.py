"""
Fichier : corpse.py
Auteur : base technique (game jam)

Description :
Le cadavre : la mécanique centrale du jeu.

Un cadavre issu d'une mort VOLONTAIRE (fiole ou piège) reste dans le niveau et :
  - émet une faible lueur, ce qui en fait un repère dans le noir ;
  - conserve l'inventaire que le joueur transportait, récupérable plus tard ;
  - a une présence physique : il maintient une plaque de pression enfoncée et
    arrête les projectiles, tout en restant franchissable (on marche dessus,
    il ne bouche jamais un couloir).

Un joueur dévoré par la créature ne laisse AUCUN cadavre : c'est toute la
différence entre choisir sa mort et la subir.
"""
from __future__ import annotations

import math

import arcade

from src import constants as C
from src.entities.items import Item
from src.entities.textures import centered_box, load_single


class Corpse(arcade.Sprite):
    """Dépouille persistante laissée par une mort volontaire."""

    def __init__(self, center_x: float, center_y: float, items: list[Item],
                 cause: str = C.DEATH_VIAL):
        super().__init__(
            load_single("corpse.png", tuple(centered_box(28, 28))),
            center_x=center_x,
            center_y=center_y,
        )
        self.items: list[Item] = list(items)
        self.cause = cause
        self.age = 0.0
        # Décalage de phase, pour que les cadavres ne pulsent pas en choeur.
        self._phase = (center_x * 0.013 + center_y * 0.017) % (math.pi * 2)

    @property
    def has_items(self) -> bool:
        return bool(self.items)

    def take_item(self) -> Item | None:
        """Retire et renvoie le premier objet encore présent sur la dépouille."""
        if not self.items:
            return None
        return self.items.pop(0)

    def light_intensity(self) -> float:
        """Pulsation lente de la lueur (utilisée par le moteur de lumière)."""
        return 0.85 + 0.15 * math.sin(self.age * 1.6 + self._phase)

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.age += delta_time
