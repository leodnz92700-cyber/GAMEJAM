"""
Fichier : npc.py
Auteur : [À COMPLÉTER — module laissé volontairement minimal]

Description :
Les PNJ du labyrinthe. Pour l'instant : un sprite qui affiche une réplique
quand le joueur interagit avec lui. Aucun PNJ n'est posé dans les cartes
placeholder ; ajoutez des objets de classe "npc" dans le calque "NPCs" sous
Tiled pour en faire apparaître.

Piste d'évolution (le pitch mentionne des PNJ qui demandent des objets) :
ajoutez une propriété Tiled `wants_item` et faites que `interaction_manager`
consomme l'objet correspondant avant de déclencher un effet (ouvrir une porte,
donner une clé, révéler un passage).
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
        self.satisfied = False
        self._line_index = 0

    def next_line(self) -> str:
        """Réplique suivante, en boucle sur la dernière."""
        line = self.lines[min(self._line_index, len(self.lines) - 1)]
        self._line_index = min(self._line_index + 1, len(self.lines) - 1)
        return line
