"""
Fichier : npc.py
Auteur : [À COMPLÉTER — module laissé volontairement minimal]

Description :
Les PNJ du labyrinthe : un sprite avec lequel on dialogue, et qui peut réclamer
un objet (propriété Tiled `wants_item`).

Le troc est SANS ÉTAT et se rejoue autant de fois qu'on veut : à chaque fois que
le joueur se présente avec l'objet demandé, le PNJ le prend et rend une clé.
C'est voulu — les clés se dupliquent comme le reste, le PNJ est une source, pas
une étape franchie une fois pour toutes. Il n'y a donc aucun drapeau « déjà
servi » ici : ce que dit le PNJ ne dépend que de ce que le joueur porte AU
MOMENT où il lui parle.

C'est `interaction_manager._talk` qui exécute l'échange ; ici on ne garde que les
répliques.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.textures import centered_box, load_strip


class NPC(arcade.Sprite):
    """Personnage non-joueur avec lequel on peut dialoguer."""

    def __init__(self, center_x: float, center_y: float, lines: list[str] | None = None,
                 wants_item: str | None = None):
        frame_width, frame_height = C.PLAYER_FRAME_SIZE
        super().__init__(
            load_strip(
                "npc_idle.png",
                frame_width,
                frame_height,
                tuple(centered_box(20, 16)),
                lift=C.PLAYER_ART_LIFT,
            )[0],
            center_x=center_x,
            center_y=center_y,
        )
        self.lines = lines or ["..."]
        self.wants_item = wants_item
        self._line_index = 0

    def next_line(self) -> str:
        """Réplique suivante, en boucle sur la dernière."""
        line = self.lines[min(self._line_index, len(self.lines) - 1)]
        self._line_index = min(self._line_index + 1, len(self.lines) - 1)
        return line
