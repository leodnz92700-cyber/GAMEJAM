"""
Fichier : victory_view.py
Auteur : base technique (game jam)

Description :
Écran de victoire : le joueur a trouvé la sortie du labyrinthe.

La mise en page est celle de `end_screen.py`, partagée avec l'écran de défaite.
Seuls le titre et la phrase de verdict sont propres à la victoire : ils parlent
du rapport entre les morts choisies et les morts subies, parce que c'est la
lecture la plus parlante du theme.
"""
from __future__ import annotations

import arcade
from src.camera_utils import apply_letterbox

from src import constants as C
from src.mechanics.audio_manager import AudioManager
from src.views.end_screen import draw_end_screen


class VictoryView(arcade.View):
    """Écran de fin de partie gagnée."""

    def __init__(self, stats):
        super().__init__()
        self.camera = arcade.Camera2D(viewport=arcade.LBWH(0,0,C.WINDOW_WIDTH,C.WINDOW_HEIGHT))
        self.stats = stats
        self.audio = AudioManager()

    def on_show_view(self) -> None:
        self.on_resize(self.window.width, self.window.height)
        self.window.background_color = C.COLOR_BACKGROUND
        # La fanfare de sortie une fois, puis la musique du menu : l'ecran de fin
        # et l'ecran d'accueil sonnent pareil, et le son ne se coupe pas entre
        # les deux.
        self.audio.play("victory")
        self.audio.start_menu_music()

    def on_hide_view(self) -> None:
        self.audio.stop_all()

    def on_key_press(self, key: int, modifiers: int) -> None:
        from src.views.main_menu import MainMenuView

        if key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE,
                   arcade.key.ESCAPE):
            self.audio.play("ui_click")
            self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        draw_end_screen(
            "TU ES SORTI",
            C.COLOR_ACCENT,
            self._verdict(),
            C.COLOR_TEXT,
            self.stats,
        )

    def _verdict(self) -> str:
        """Une phrase qui juge la partie, pas un simple decompte."""
        chosen = self.stats.deaths_by_vial + self.stats.deaths_by_trap
        if self.stats.deaths_devoured == 0 and chosen > 0:
            return "Tu n'as jamais ete pris. Chacune de tes morts etait la tienne."
        if chosen == 0:
            return "Sorti sans jamais te sacrifier. La tour t'a laisse passer."
        return f"{chosen} morts choisies, {self.stats.deaths_devoured} subies."

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        apply_letterbox(self.camera, width, height)
