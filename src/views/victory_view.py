"""
Fichier : victory_view.py
Auteur : base technique (game jam)

Description :
Écran de victoire : le joueur a atteint le sommet de la tour.

Les statistiques racontent la partie, et surtout le rapport entre les morts
choisies (fioles, pieges) et les morts subies (devore). C'est la lecture la plus
parlante du theme.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached
from src.ui.menu_components import draw_hint, draw_title


class VictoryView(arcade.View):
    """Écran de fin de partie gagnée."""

    def __init__(self, stats):
        super().__init__()
        self.stats = stats

    def on_show_view(self) -> None:
        self.window.background_color = C.COLOR_BACKGROUND

    def on_key_press(self, key: int, modifiers: int) -> None:
        from src.views.main_menu import MainMenuView

        if key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE,
                   arcade.key.ESCAPE):
            self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.clear()
        draw_title("TU ES SORTI", C.WINDOW_HEIGHT - 140, 46)

        chosen = self.stats.deaths_by_vial + self.stats.deaths_by_trap
        draw_text_cached(
            f"{chosen} morts choisies, {self.stats.deaths_devoured} subies.",
            C.WINDOW_WIDTH / 2,
            C.WINDOW_HEIGHT - 190,
            C.COLOR_ACCENT,
            18,
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
