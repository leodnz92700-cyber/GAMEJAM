"""
Fichier : menu_components.py
Auteur : base technique (game jam)

Description :
Briques d'interface réutilisées par les écrans : bouton, liste de boutons
navigable au clavier ET à la souris, et petits utilitaires de titre.

Les menus du jeu se pilotent entièrement au clavier (fleches + Entree), la
souris n'étant qu'un confort : dans le noir, on ne cherche pas son curseur.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached


class Button:
    """Un bouton rectangulaire avec un libellé et une description optionnelle."""

    def __init__(self, label: str, x: float, y: float, width: float = 520,
                 height: float = 52, description: str = "", value=None):
        self.label = label
        self.description = description
        self.value = value
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height

    def contains(self, x: float, y: float) -> bool:
        return (
            abs(x - self.center_x) <= self.width / 2
            and abs(y - self.center_y) <= self.height / 2
        )

    def draw(self, selected: bool) -> None:
        background = (34, 32, 44) if selected else (20, 20, 26)
        border = C.COLOR_ACCENT if selected else C.COLOR_HUD_BORDER
        arcade.draw_lbwh_rectangle_filled(
            self.center_x - self.width / 2,
            self.center_y - self.height / 2,
            self.width,
            self.height,
            background,
        )
        arcade.draw_lbwh_rectangle_outline(
            self.center_x - self.width / 2,
            self.center_y - self.height / 2,
            self.width,
            self.height,
            border,
            2,
        )
        draw_text_cached(
            self.label,
            self.center_x - self.width / 2 + 18,
            self.center_y + 2,
            C.COLOR_TEXT if selected else C.COLOR_TEXT_DIM,
            16,
        )
        if self.description:
            draw_text_cached(
                self.description,
                self.center_x - self.width / 2 + 18,
                self.center_y - 19,
                C.COLOR_TEXT_DIM,
                11,
            )


class ButtonList:
    """Liste verticale de boutons avec un curseur de sélection."""

    def __init__(self, buttons: list[Button]):
        self.buttons = buttons
        self.selected = 0

    @property
    def current(self) -> Button:
        return self.buttons[self.selected]

    def move(self, step: int) -> None:
        if not self.buttons:
            return
        self.selected = (self.selected + step) % len(self.buttons)

    def on_mouse_motion(self, x: float, y: float) -> None:
        for index, button in enumerate(self.buttons):
            if button.contains(x, y):
                self.selected = index
                return

    def on_mouse_press(self, x: float, y: float) -> Button | None:
        for index, button in enumerate(self.buttons):
            if button.contains(x, y):
                self.selected = index
                return button
        return None

    def draw(self) -> None:
        for index, button in enumerate(self.buttons):
            button.draw(index == self.selected)


def draw_title(text: str, y: float, size: int = 44) -> None:
    draw_text_cached(
        text,
        C.WINDOW_WIDTH / 2,
        y,
        C.COLOR_ACCENT,
        size,
        anchor_x="center",
        bold=True,
    )


def draw_hint(text: str, y: float = 28) -> None:
    draw_text_cached(
        text,
        C.WINDOW_WIDTH / 2,
        y,
        C.COLOR_TEXT_DIM,
        12,
        anchor_x="center",
    )
