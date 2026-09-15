"""
Fichier : main_menu.py
Auteur : base technique (game jam)

Description :
Écran d'accueil : le lore, le choix du mode de jeu, l'accès à la sélection
d'étage, et le tableau des scores local.

Navigation : fleches haut/bas pour changer de ligne, fleches gauche/droite pour
changer la valeur d'une ligne (le mode de jeu), Entree pour valider. La souris
fonctionne aussi.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached
from src.mechanics.audio_manager import AudioManager
from src.mechanics.score_manager import ScoreManager
from src.ui.dialog_box import DialogBox
from src.ui.menu_components import Button, ButtonList, draw_hint, draw_title

LORE = (
    "Tu te reveilles au pied d'une tour dont chaque etage est un labyrinthe sans "
    "lumiere. Tu ne sais pas comment tu es entre, seulement qu'il faut monter.\n\n"
    "REGLES DU JEU :\n"
    "E: Interagir (ramasser, fouiller, ouvrir)   F: Planter torche   R: Boire fiole\n\n"
    "Bois une fiole et tu meurs sur-le-champ : ton corps reste la ou il tombe, "
    "il brille faiblement, et il garde ce que tu portais.\n\n"
    "Quelque chose rode dans la tour... "
    "Si elle te prend, il ne restera rien de toi."
)

# Ordre d'affichage des modes dans le menu.
MODE_ORDER = [C.MODE_FREE, C.MODE_LIMITED_DEATHS, C.MODE_TIMED]


class MainMenuView(arcade.View):
    """Écran d'accueil."""

    def __init__(self, mode_index: int = 0, level_index: int = 0):
        super().__init__()
        self.mode_index = mode_index
        self.level_index = level_index

        self.audio = AudioManager()
        self.score = ScoreManager()
        self.leaderboard = self.score.load_leaderboard()

        self.lore_box = DialogBox(320, C.WINDOW_HEIGHT - 300, 580, 260, font_size=13)
        self.lore_box.show(LORE)

        self.buttons = ButtonList(
            [
                Button("", 320, 268, 580, 54),   # mode (libellé recalculé à chaque frame)
                Button("", 320, 204, 580, 54),   # étage de depart
                Button("Entrer dans la tour", 320, 140, 580, 54),
                Button("Quitter", 320, 76, 580, 54),
            ]
        )
        self._refresh_labels()

    def on_show_view(self) -> None:
        self.window.background_color = C.COLOR_BACKGROUND
        self.leaderboard = self.score.load_leaderboard()
        self.audio.start_ambience()

    def on_hide_view(self) -> None:
        self.audio.stop_ambience()

    # ------------------------------------------------------------------ #
    # État du menu
    # ------------------------------------------------------------------ #
    @property
    def mode(self) -> str:
        return MODE_ORDER[self.mode_index]

    def _refresh_labels(self) -> None:
        mode = C.GAME_MODES[self.mode]
        self.buttons.buttons[0].label = f"Mode : {mode['label']}   (< >)"
        self.buttons.buttons[0].description = mode["description"]
        self.buttons.buttons[1].label = f"Etage de depart : {self.level_index + 1}"
        self.buttons.buttons[1].description = (
            f"{len(C.LEVELS)} etages disponibles. Entree pour choisir."
        )

    # ------------------------------------------------------------------ #
    # Entrées
    # ------------------------------------------------------------------ #
    def on_key_press(self, key: int, modifiers: int) -> None:
        if key in (arcade.key.DOWN, arcade.key.S):
            self.buttons.move(1)
        elif key in (arcade.key.UP, arcade.key.Z):
            self.buttons.move(-1)
        elif key in (arcade.key.LEFT, arcade.key.Q) and self.buttons.selected == 0:
            self.mode_index = (self.mode_index - 1) % len(MODE_ORDER)
            self._refresh_labels()
        elif key in (arcade.key.RIGHT, arcade.key.D) and self.buttons.selected == 0:
            self.mode_index = (self.mode_index + 1) % len(MODE_ORDER)
            self._refresh_labels()
        elif key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE):
            self._activate(self.buttons.selected)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        self.buttons.on_mouse_motion(x, y)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.buttons.on_mouse_press(x, y) is not None:
            self._activate(self.buttons.selected)

    def _activate(self, index: int) -> None:
        if index == 0:
            self.mode_index = (self.mode_index + 1) % len(MODE_ORDER)
            self._refresh_labels()
        elif index == 1:
            from src.views.level_select import LevelSelectView

            self.window.show_view(LevelSelectView(self.mode_index, self.level_index))
        elif index == 2:
            self._start_game()
        elif index == 3:
            arcade.close_window()

    def _start_game(self) -> None:
        from src.views.game_view import GameView

        self.audio.stop_ambience()
        game = GameView(mode=self.mode, level_index=self.level_index)
        game.setup()
        self.window.show_view(game)

    # ------------------------------------------------------------------ #
    # Rendu
    # ------------------------------------------------------------------ #
    def on_draw(self) -> None:
        self.clear()
        draw_title("LABYRINTH OF SHADOW", C.WINDOW_HEIGHT - 90, 46)
        draw_text_cached(
            "Mourir pour mieux avancer",
            C.WINDOW_WIDTH / 2,
            C.WINDOW_HEIGHT - 128,
            C.COLOR_TEXT_DIM,
            16,
            anchor_x="center",
            italic=True,
        )
        self.lore_box.draw()
        self.buttons.draw()
        self._draw_leaderboard()
        draw_hint("Fleches : naviguer     Entree : valider     Echap : quitter")

    def _draw_leaderboard(self) -> None:
        left = 700
        arcade.draw_lbwh_rectangle_outline(
            left, 76, 540, C.WINDOW_HEIGHT - 240, C.COLOR_HUD_BORDER, 2
        )
        draw_text_cached(
            "TABLEAU DES SCORES (local)", left + 22, C.WINDOW_HEIGHT - 190,
            C.COLOR_ACCENT, 15,
        )
        if not self.leaderboard:
            draw_text_cached(
                "Aucune partie enregistree.\nLa premiere tentative fera date.",
                left + 22,
                C.WINDOW_HEIGHT - 240,
                C.COLOR_TEXT_DIM,
                13,
                multiline=True,
                width=480,
            )
            return

        header_y = C.WINDOW_HEIGHT - 226
        draw_text_cached(
            f"{'issue':<10}{'temps':<9}{'morts':<8}{'devore':<9}{'torches':<9}mode",
            left + 22, header_y, C.COLOR_TEXT_DIM, 12,
        )
        for index, run in enumerate(self.leaderboard[:12]):
            minutes, seconds = divmod(int(run.get("elapsed", 0)), 60)
            issue = "VICTOIRE" if run.get("victory") else "echec"
            mode_label = C.GAME_MODES.get(run.get("mode", ""), {}).get("label", "?")
            draw_text_cached(
                f"{issue:<10}{minutes:02d}:{seconds:02d}    "
                f"{run.get('deaths_total', 0):<8}{run.get('deaths_devoured', 0):<9}"
                f"{run.get('torches_placed', 0):<9}{mode_label}",
                left + 22,
                header_y - 26 - index * 22,
                C.COLOR_TEXT if run.get("victory") else C.COLOR_TEXT_DIM,
                12,
            )
