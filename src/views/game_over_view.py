"""
Fichier : game_over_view.py
Auteur : base technique (game jam)

Description :
Écran de défaite. Il n'apparaît que dans les modes qui autorisent un échec :
en mode Exploration, le joueur meurt sans jamais perdre.

On affiche les mêmes statistiques que l'écran de victoire : le but est que le
joueur reparte en sachant combien de morts lui ont vraiment servi.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached
from src.ui.menu_components import draw_hint, draw_title


class GameOverView(arcade.View):
    """Écran de fin de partie perdue."""

    def __init__(self, stats, reason: str = ""):
        super().__init__()
        self.stats = stats
        self.reason = reason

    def on_show_view(self) -> None:
        self.window.background_color = C.COLOR_BACKGROUND

    def on_key_press(self, key: int, modifiers: int) -> None:
        from src.views.main_menu import MainMenuView

        if key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE,
                   arcade.key.ESCAPE):
            self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.clear()
        draw_title("LA TOUR TE GARDE", C.WINDOW_HEIGHT - 140, 42)
        if self.reason:
            draw_text_cached(
                self.reason,
                C.WINDOW_WIDTH / 2,
                C.WINDOW_HEIGHT - 190,
                C.COLOR_DANGER,
                17,
                anchor_x="center",
                italic=True,
            )

        top = C.WINDOW_HEIGHT - 260
        for index, (label, value) in enumerate(self.stats.as_lines()):
            y = top - index * 28
            draw_text_cached(label, C.WINDOW_WIDTH / 2 - 260, y, C.COLOR_TEXT_DIM, 14)
            draw_text_cached(value, C.WINDOW_WIDTH / 2 + 200, y, C.COLOR_TEXT, 14,
                             anchor_x="right")

        draw_hint("Entree : retour a l'ecran d'accueil")
