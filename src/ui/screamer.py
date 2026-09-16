"""
Fichier : screamer.py
Auteur : base technique (game jam)

Description :
Le jumpscare joué quand la créature dévore le joueur.

C'est la mort la plus punitive du jeu — aucun cadavre, aucun objet, aucun
nouveau repère — et elle passait jusqu'ici presque inaperçue : écran noir, puis
on recommence. Cet écran lui donne enfin son poids, et il apprend au joueur à
craindre les bruits qui l'annoncent.

Trois temps, réglables dans `constants.py` :
  1. un éclair blanc très bref ;
  2. la gueule du fantôme qui remplit l'écran, qui tremble et qui grossit ;
  3. un fondu au noir, juste avant la vie suivante.

L'écran couvre toute la fenêtre ; l'ATH reste dessiné par-dessus.
"""
from __future__ import annotations

import math
import random

import arcade

from src import constants as C
from src.entities.textures import load_strip


class Screamer:
    """Surimpression plein écran jouée à la mort par dévoration."""

    def __init__(self):
        frame_width, frame_height = C.MONSTER_FRAME_SIZE
        self.frames = load_strip("monster_attack.png", frame_width, frame_height)
        self.elapsed = 0.0
        self.active = False
        self._rng = random.Random()

    # ------------------------------------------------------------------ #
    # Cycle de vie
    # ------------------------------------------------------------------ #
    def start(self) -> None:
        self.elapsed = 0.0
        self.active = True

    def stop(self) -> None:
        self.active = False
        self.elapsed = 0.0

    @property
    def finished(self) -> bool:
        return self.elapsed >= C.SCREAMER_DURATION

    def update(self, delta_time: float) -> None:
        if not self.active:
            return
        self.elapsed += delta_time
        if self.finished:
            self.active = False

    # ------------------------------------------------------------------ #
    # Rendu (coordonnées écran, caméra GUI active)
    # ------------------------------------------------------------------ #
    def draw(self) -> None:
        if not self.active:
            return
        if self.elapsed < C.SCREAMER_FLASH_DURATION:
            self._draw_flash()
        elif self.elapsed < C.SCREAMER_FLASH_DURATION + C.SCREAMER_FACE_DURATION:
            self._draw_face()
        else:
            self._draw_face()
            self._draw_fade_out()

    def _viewport(self, alpha: int, color=(0, 0, 0)) -> None:
        arcade.draw_lbwh_rectangle_filled(
            0, 0, C.WINDOW_WIDTH, C.WINDOW_HEIGHT, (*color, alpha)
        )

    def _draw_flash(self) -> None:
        """Éclair blanc : le joueur n'a rien vu venir, l'écran non plus."""
        progress = self.elapsed / C.SCREAMER_FLASH_DURATION
        self._viewport(int(255 * (1.0 - progress * 0.45)), (255, 250, 245))

    def _draw_face(self) -> None:
        """La gueule du fantôme, qui grossit et tremble."""
        phase = min(
            1.0,
            max(0.0, (self.elapsed - C.SCREAMER_FLASH_DURATION) / C.SCREAMER_FACE_DURATION),
        )
        # Fond rouge sombre, qui s'assombrit au fil de la seconde.
        self._viewport(int(225 - 40 * phase), (26, 4, 6))

        frame = self.frames[int(self.elapsed * 18) % len(self.frames)]
        # Le visage grossit franchement : c'est ce qui fait sursauter.
        height = C.VIEWPORT_HEIGHT * (0.72 + 0.38 * phase)
        width = height * frame.width / frame.height
        shake = C.SCREAMER_SHAKE * (1.0 - phase * 0.4)
        offset_x = math.sin(self.elapsed * 47.0) * shake + self._rng.uniform(-4, 4)
        offset_y = math.cos(self.elapsed * 39.0) * shake * 0.6

        center_x = C.WINDOW_WIDTH / 2 + offset_x
        center_y = C.WINDOW_HEIGHT / 2 + offset_y
        arcade.draw_texture_rect(
            frame,
            arcade.LBWH(center_x - width / 2, center_y - height / 2, width, height),
            pixelated=True,
        )

    def _draw_fade_out(self) -> None:
        elapsed_in_fade = (
            self.elapsed - C.SCREAMER_FLASH_DURATION - C.SCREAMER_FACE_DURATION
        )
        progress = min(1.0, elapsed_in_fade / C.SCREAMER_FADE_DURATION)
        self._viewport(int(255 * progress))
