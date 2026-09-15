"""
Fichier : level_select.py
Auteur : base technique (game jam)

Description :
Sélection de l'étage de départ. Utile surtout pendant le développement : chacun
peut lancer directement l'étage sur lequel il travaille sans retraverser les
precedents.

La carte de test (`level_test.tmx`) est proposée en plus des vrais étages.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached
from src.ui.menu_components import Button, ButtonList, draw_hint, draw_title


class LevelSelectView(arcade.View):
    """Choix de l'étage de départ."""

    def __init__(self, mode_index: int = 0, level_index: int = 0):
        super().__init__()
        self.mode_index = mode_index
        self.level_index = level_index

        buttons = []
        top = C.WINDOW_HEIGHT - 260
        for index, level_name in enumerate(C.LEVELS):
            buttons.append(
                Button(
                    f"Etage {index + 1}",
                    C.WINDOW_WIDTH / 2,
                    top - index * 68,
                    620,
                    56,
                    description=f"carte : {level_name}",
                    value=index,
                )
            )
        buttons.append(
            Button(
                "Retour",
                C.WINDOW_WIDTH / 2,
                top - len(C.LEVELS) * 68 - 20,
                620,
                56,
                description="revenir a l'ecran d'accueil",
                value=None,
            )
        )
        self.buttons = ButtonList(buttons)
        self.buttons.selected = min(level_index, len(buttons) - 1)

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key in (arcade.key.DOWN, arcade.key.S):
            self.buttons.move(1)
        elif key in (arcade.key.UP, arcade.key.Z):
            self.buttons.move(-1)
        elif key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE):
            self._activate()
        elif key == arcade.key.ESCAPE:
            self._back(self.level_index)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        self.buttons.on_mouse_motion(x, y)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.buttons.on_mouse_press(x, y) is not None:
            self._activate()

    def _activate(self) -> None:
        value = self.buttons.current.value
        self._back(self.level_index if value is None else value)

    def _back(self, level_index: int) -> None:
        from src.views.main_menu import MainMenuView

        self.window.show_view(MainMenuView(self.mode_index, level_index))

    def on_draw(self) -> None:
        self.clear()
        draw_title("CHOISIR UN ETAGE", C.WINDOW_HEIGHT - 140, 34)
        draw_text_cached(
            "Chaque etage est une carte Tiled independante (assets/maps).",
            C.WINDOW_WIDTH / 2,
            C.WINDOW_HEIGHT - 186,
            C.COLOR_TEXT_DIM,
            13,
            anchor_x="center",
        )
        self.buttons.draw()
        draw_hint("Fleches : naviguer     Entree : valider     Echap : retour")
