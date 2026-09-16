"""
Fichier : game_over_view.py
Auteur : base technique (game jam)

Description :
Écran de défaite. Il n'apparaît que dans les modes qui autorisent un échec :
en mode Exploration, le joueur meurt sans jamais perdre.

Même mise en page que la victoire (`end_screen.py`), volontairement : le joueur
doit pouvoir comparer d'un coup d'oeil deux parties, celle qu'il a perdue et
celle qu'il a gagnee. Seuls le titre et sa couleur changent.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.views.end_screen import draw_end_screen


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
        draw_end_screen(
            "LA TOUR TE GARDE",
            C.COLOR_DANGER,
            self.reason,
            C.COLOR_DANGER,
            self.stats,
        )
