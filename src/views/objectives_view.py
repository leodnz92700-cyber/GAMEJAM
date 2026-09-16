"""
Fichier : objectives_view.py

Description :
Ecran des objectifs affiche entre le menu et le jeu. Le joueur lit la liste
des choses a faire, puis appuie sur une touche pour demarrer la partie.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.views.game_view import GameView

OBJECTIVES = [
    "1. Prends la potion",
    "2. Suicide toi sur les plaques de pressions",
    "3. Cherche le bouclier",
    "4. Donne le au mage pour prendre la cle",
    "5. Cherche la sortie",
    "6. Ouvre la porte de la salle et sort",
]


class ObjectivesView(arcade.View):
    """Ecran intermediaire affichant les objectifs et servant de pause."""

    def __init__(self, game_view: GameView):
        super().__init__()
        self.game_view = game_view

    def on_show_view(self) -> None:
        self.window.background_color = C.COLOR_BACKGROUND

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            from src.views.main_menu import MainMenuView
            self.window.show_view(MainMenuView())
            return
        if key in (arcade.key.O, arcade.key.ENTER):
            self.window.show_view(self.game_view)

    def on_draw(self) -> None:
        self.clear()

        cx = C.WINDOW_WIDTH / 2
        top = C.WINDOW_HEIGHT - 120

        draw_text_cached(
            "OBJECTIFS (PAUSE)",
            cx, top, C.COLOR_ACCENT, 32,
            anchor_x="center", bold=True,
        )

        line_y = top - 70
        for line in OBJECTIVES:
            draw_text_cached(
                line, cx, line_y, C.COLOR_TEXT, 20,
                anchor_x="center",
            )
            line_y -= 40

        draw_text_cached(
            "Appuie sur O ou Entree pour reprendre",
            cx, 60, C.COLOR_TEXT_DIM, 16,
            anchor_x="center", italic=True,
        )
