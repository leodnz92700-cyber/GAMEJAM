"""
Fichier : torch.py
Auteur : base technique (game jam)

Description :
Les torches plantées au sol. Contrairement au halo du joueur, leur lumière est
permanente : c'est le seul moyen pour le joueur de transformer durablement le
labyrinthe, et donc de rendre les vies suivantes plus lisibles.

Une torche plantée ne se ramasse plus. En revanche, une torche encore dans
l'inventaire au moment d'une mort volontaire se retrouve sur le cadavre et peut
être reprise plus tard — mais elle est perdue si la créature dévore le corps.

Elles vacillent en permanence, et beaucoup plus fort quand la créature approche :
le vacillement fait partie des signaux d'alerte (voir monster_manager).
"""
from __future__ import annotations

import math
import random

import arcade

from src import constants as C
from src.entities.textures import load_strip


class Torch(arcade.Sprite):
    """Torche plantée dans le labyrinthe, source de lumière permanente."""

    def __init__(self, center_x: float, center_y: float):
        # Pas de boîte de collision utile : on marche sur une torche plantée.
        self.frames = load_strip("torch_strip.png", C.TILE_SIZE, C.TILE_SIZE)
        super().__init__(self.frames[0], center_x=center_x, center_y=center_y)

        self.radius = C.TORCH_LIGHT_RADIUS
        self._time = random.uniform(0.0, 10.0)
        self._noise = random.uniform(0.0, 10.0)
        self._frame_index = random.uniform(0.0, len(self.frames))
        # Réglé par monster_manager : 0 = calme, 1 = la créature est sur le point
        # de surgir. Plus la valeur est haute, plus la flamme est instable.
        self.panic = 0.0

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self._time += delta_time
        # La flamme s'agite quand la créature approche.
        fps = C.TORCH_FPS * (1.0 + self.panic * 1.5)
        self._frame_index = (self._frame_index + delta_time * fps) % len(self.frames)
        self.texture = self.frames[int(self._frame_index)]

    def light_intensity(self) -> float:
        """Facteur multiplicatif appliqué au rayon lumineux (autour de 1.0)."""
        amplitude = C.FLICKER_AMPLITUDE + self.panic * (
            C.FLICKER_PANIC_AMPLITUDE - C.FLICKER_AMPLITUDE
        )
        wobble = (
            math.sin(self._time * 11.0 + self._noise)
            + 0.6 * math.sin(self._time * 23.0 + self._noise * 2)
        ) / 1.6
        return 1.0 + wobble * amplitude
