"""
Fichier : dialog_box.py
Auteur : base technique (game jam)

Description :
Encadré de texte : sert au lore de l'écran d'accueil et aux répliques des PNJ.

Volontairement rustique (un rectangle et du texte multiligne) : c'est suffisant
pour une jam, et ça ne dépend d'aucune ressource graphique.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached


class DialogBox:
    """Panneau de texte, optionnellement temporisé."""

    def __init__(self, x: float, y: float, width: float, height: float,
                 font_size: int = 14):
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.text = ""
        self.timer = 0.0

    def show(self, text: str, duration: float = 0.0) -> None:
        """Affiche un texte. `duration` à 0 = affichage permanent."""
        self.text = text
        self.timer = duration

    def clear(self) -> None:
        self.text = ""
        self.timer = 0.0

    @property
    def visible(self) -> bool:
        return bool(self.text)

    def update(self, delta_time: float) -> None:
        if self.timer <= 0:
            return
        self.timer -= delta_time
        if self.timer <= 0:
            self.clear()

    def draw(self) -> None:
        if not self.visible:
            return
        left = self.center_x - self.width / 2
        bottom = self.center_y - self.height / 2
        arcade.draw_lbwh_rectangle_filled(
            left, bottom, self.width, self.height, C.COLOR_PANEL_FILL
        )
        arcade.draw_lbwh_rectangle_outline(
            left, bottom, self.width, self.height, C.COLOR_HUD_BORDER, 2
        )
        draw_text_cached(
            self.text,
            left + 22,
            self.center_y + self.height / 2 - 34,
            C.COLOR_TEXT,
            self.font_size,
            width=int(self.width - 44),
            multiline=True,
        )
