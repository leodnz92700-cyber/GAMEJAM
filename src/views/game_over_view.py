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
from src.camera_utils import apply_letterbox

from src import constants as C
from src.mechanics.audio_manager import AudioManager
from src.views.end_screen import draw_end_screen


class GameOverView(arcade.View):
    """Écran de fin de partie perdue."""

    def __init__(self, stats, reason: str = ""):
        super().__init__()
        self.camera = arcade.Camera2D(viewport=arcade.LBWH(0,0,C.WINDOW_WIDTH,C.WINDOW_HEIGHT))
        self.stats = stats
        self.audio = AudioManager()
        self.reason = reason
        self.fade_in = 0.5
        self.fade_out = 0.0
        self.next_view = None

    def on_show_view(self) -> None:
        self.on_resize(self.window.width, self.window.height)
        self.window.background_color = C.COLOR_BACKGROUND
        self.audio.play("game_over")
        self.audio.start_menu_music()

    def on_hide_view(self) -> None:
        self.audio.stop_all()
        
    def on_update(self, delta_time: float) -> None:
        if self.fade_in > 0:
            self.fade_in = max(0.0, self.fade_in - delta_time)
        if self.fade_out > 0:
            self.fade_out -= delta_time
            if self.fade_out <= 0 and self.next_view:
                self.window.show_view(self.next_view)

    def on_key_press(self, key: int, modifiers: int) -> None:
        from src.views.main_menu import MainMenuView

        if key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE,
                   arcade.key.ESCAPE):
            if self.fade_out > 0:
                return
            self.audio.play("ui_click")
            self.fade_out = 0.5
            self.next_view = MainMenuView()

    def on_draw(self) -> None:
        self.clear()
        self.camera.use()
        draw_end_screen(
            "LA TOUR TE GARDE",
            C.COLOR_DANGER,
            self.reason,
            C.COLOR_DANGER,
            self.stats,
        )
        
        alpha = 0
        if self.fade_in > 0:
            alpha = int((self.fade_in / 0.5) * 255)
        elif self.fade_out > 0:
            alpha = int((1.0 - self.fade_out / 0.5) * 255)
        
        if alpha > 0:
            arcade.draw_lbwh_rectangle_filled(
                0, 0, C.WINDOW_WIDTH, C.WINDOW_HEIGHT, (0, 0, 0, alpha)
            )

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        apply_letterbox(self.camera, width, height)
