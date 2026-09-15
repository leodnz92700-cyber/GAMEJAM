"""
Fichier : monster.py
Auteur : base technique (game jam)

Description :
La créature : un fantôme (sprite du pack) qui n'existe physiquement qu'une fois
lâché dans le labyrinthe. Avant cela, seule l'ambiance sonore signale son
approche (voir monster_manager).

Volontairement pauvre en logique : elle se contente de suivre le chemin que
`monster_manager` lui calcule. Toute la mise en scène (sons, vacillement des
torches, apparition fugitive) est gérée ailleurs.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.textures import centered_box, load_strip


class Monster(arcade.Sprite):
    """Prédateur qui traque le joueur une fois le sursis écoulé."""

    def __init__(self, center_x: float, center_y: float):
        frame_width, frame_height = C.MONSTER_FRAME_SIZE
        box = tuple(centered_box(26, 26))
        self.idle_frames = load_strip("monster_idle.png", frame_width, frame_height, box)
        self.move_frames = load_strip("monster_move.png", frame_width, frame_height, box)
        super().__init__(self.idle_frames[0], center_x=center_x, center_y=center_y)

        self.path: list[tuple[float, float]] = []
        self.speed = C.MONSTER_SPEED
        self._frame_index = 0.0
        # On ne la dessine qu'à très courte distance : le reste du temps, le
        # joueur ne doit avoir que le son pour se repérer.
        self.alpha = 0

    def follow_path(self, delta_time: float) -> None:
        """Avance le long du chemin calculé, point par point."""
        if not self.path:
            return
        target_x, target_y = self.path[0]
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = (dx * dx + dy * dy) ** 0.5
        if distance < 4.0:
            self.path.pop(0)
            return
        step = self.speed * delta_time
        if step >= distance:
            self.position = (target_x, target_y)
            self.path.pop(0)
            return
        self.center_x += dx / distance * step
        self.center_y += dy / distance * step

    def update_animation(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        frames = self.move_frames if self.path else self.idle_frames
        self._frame_index = (self._frame_index + delta_time * C.MONSTER_FPS) % len(frames)
        self.texture = frames[int(self._frame_index)]

    def update_visibility(self, player_x: float, player_y: float) -> None:
        """Fait apparaître une silhouette seulement quand elle est très proche."""
        distance = arcade.math.get_distance(self.center_x, self.center_y, player_x, player_y)
        if distance > C.MONSTER_VISIBLE_RADIUS:
            self.alpha = 0
            return
        ratio = 1.0 - (distance / C.MONSTER_VISIBLE_RADIUS)
        self.alpha = int(min(255, 40 + ratio * 215))
