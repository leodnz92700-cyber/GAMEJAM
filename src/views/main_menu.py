"""
Fichier : main_menu.py
Auteur : base technique (game jam)

Description :
Écran d'accueil : le logo, le lore, le choix du mode de jeu et le tableau des
scores local.

La mise en page tient en trois blocs alignés sur une grille, et c'est cette
grille qui fait tenir l'écran ensemble :

    - le LOGO occupe toute la largeur en haut, seul, sur du noir ;
    - la colonne de GAUCHE porte le lore puis les boutons ;
    - la colonne de DROITE porte le tableau des scores.

Les deux colonnes commencent et finissent exactement aux mêmes ordonnées
(`PANELS_TOP` / `PANELS_BOTTOM`) : c'est la seule façon d'obtenir deux panneaux
qui ont l'air d'appartenir au même écran.

Il n'y a **plus de selection d'etage** : le jeu ne contient qu'un seul niveau.

Navigation : fleches haut/bas pour changer de ligne, fleches gauche/droite pour
changer le mode de jeu, Entree pour valider. La souris fonctionne aussi.

**Aucun de ces rappels n'est ecrit a l'ecran** : naviguer un menu aux fleches et
valider a Entree est un reflexe acquis, l'afficher n'apprend rien et encombre le
bas de la page. Seul le choix du mode recoit un repere visuel (les trois traits
de `_draw_mode_marker`), parce que rien d'autre ne dit qu'il y a trois modes.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.mechanics.audio_manager import AudioManager
from src.mechanics.score_manager import ScoreManager
from src.ui.logo import draw_logo
from src.ui.menu_components import (
    Button,
    ButtonList,
    Column,
    draw_panel,
    draw_table,
)
from src.ui.text_cache import draw_text_cached
from src.camera_utils import apply_letterbox

# Le panneau de lore tient DOUZE lignes de 13 px, lignes vides comprises, soit
# environ 50 caracteres par ligne. Au-dela, le texte deborde par le bas sans le
# moindre avertissement : relancez l'ecran d'accueil apres l'avoir modifie.
#
# Ce texte dit explicitement les trois choses que le joueur ne peut pas deviner
# tout seul, et qui sont le jeu entier : mourir n'est pas une punition mais le
# SEUL moyen d'avancer ; le cadavre laisse sur place SERT (il eclaire, il pese
# sur les plaques) ; et surtout l'asymetrie entre les deux morts — choisie, on
# laisse un corps ; subie, on ne laisse rien.
LORE = (
    "Tu te reveilles au pied d'une tour sans lumiere. Tu n'y vois "
    "qu'a un pas devant toi.\n\n"
    "Une fiole traine pres du depart. La boire te tue sur l'instant, "
    "et c'est le seul moyen d'avancer : ton corps reste ou il tombe. "
    "Il brille. Il pese sur les plaques et ouvre les portes.\n\n"
    "Une chose rode, et elle sera lachee. Tu ne la verras pas venir : "
    "tu l'entendras. Si elle te prend, ton corps ne reste pas, et tes "
    "affaires disparaissent."
)

# Ordre d'affichage des modes dans le menu.
MODE_ORDER = [C.MODE_FREE, C.MODE_LIMITED_DEATHS, C.MODE_TIMED]

LORE_FONT_SIZE = 12

# --- La grille de l'écran --------------------------------------------------- #
MARGIN = 44
PANELS_TOP = C.WINDOW_HEIGHT - 164            # les deux colonnes commencent ici
PANELS_BOTTOM = 40          # ... et finissent ici, pres du bas de la fenetre
COLUMN_GAP = 32

# Le logo occupe la bande du haut. Le dessin est un bandeau tres etale
# (1100x160), on le contraint a rentrer dans sa boite : si on rapetisse l'ecran
# il diminue (pour eviter de chevaucher les panneaux), mais si on l'agrandit
# la boite ne le grandit plus.
LOGO_CENTER_Y = C.WINDOW_HEIGHT - 78
LOGO_MAX_WIDTH = 1000
LOGO_MAX_HEIGHT = 130

LEFT_X = MARGIN
LEFT_WIDTH = 520
RIGHT_X = LEFT_X + LEFT_WIDTH + COLUMN_GAP
RIGHT_WIDTH = C.WINDOW_WIDTH - MARGIN - RIGHT_X

BUTTON_HEIGHT = 42
BUTTON_GAP = 6
BUTTON_COUNT = 3
BUTTONS_TOP = PANELS_BOTTOM + BUTTON_COUNT * BUTTON_HEIGHT + (BUTTON_COUNT - 1) * BUTTON_GAP

LORE_BOTTOM = BUTTONS_TOP + 16

# Colonnes du tableau des scores. Les largeurs font exactement la largeur utile
# du panneau : si vous en changez une, ajustez les autres.
# Largeurs mesurees sur la police pixel a 13 px, pour le pire cas de chaque
# colonne (« VICTOIRE », « TORCHES », « Contre-la-montre »). Leur somme fait
# exactement la largeur utile du panneau : en changer une oblige a compenser
# ailleurs, sinon la derniere colonne sort du cadre.
SCORE_COLUMNS = [
    Column("issue", 86),
    Column("temps", 76, align="right"),
    Column("morts", 76, align="right"),
    Column("devore", 82, align="right"),
    Column("torches", 92, align="right"),
    Column("mode", 192),
]
SCORE_FONT_SIZE = 13
SCORE_ROWS_MAX = 15        # de quoi remplir le panneau sur toute sa hauteur
SCORE_ROW_HEIGHT = 26


class MainMenuView(arcade.View):
    """Écran d'accueil."""

    def __init__(self, mode_index: int = 0):
        super().__init__()
        self.mode_index = mode_index

        self.audio = AudioManager()
        self.score = ScoreManager()
        self.leaderboard = self.score.load_leaderboard()

        self.camera = arcade.Camera2D(
            viewport=arcade.LBWH(0, 0, C.WINDOW_WIDTH, C.WINDOW_HEIGHT)
        )

        # Les boutons sont empilés du BAS vers le haut : « Quitter » est collé
        # au bandeau d'aide, « Mode » touche le panneau de lore.
        center_x = LEFT_X + LEFT_WIDTH / 2
        labels = ["", "Entrer dans la tour", "Quitter"]
        step = BUTTON_HEIGHT + BUTTON_GAP
        self.buttons = ButtonList(
            [
                Button(
                    label,
                    center_x,
                    BUTTONS_TOP - BUTTON_HEIGHT / 2 - index * step,
                    LEFT_WIDTH,
                    BUTTON_HEIGHT,
                )
                for index, label in enumerate(labels)
            ]
        )
        self.buttons.buttons[1].description = "une seule tour, une seule sortie"
        self.buttons.buttons[2].description = "fermer le jeu"
        self._refresh_labels()

    def on_show_view(self) -> None:
        self.on_resize(self.window.width, self.window.height)
        self.window.background_color = C.COLOR_BACKGROUND
        self.leaderboard = self.score.load_leaderboard()
        self.audio.start_menu_music()

    def on_hide_view(self) -> None:
        self.audio.stop_all()

    # ------------------------------------------------------------------ #
    # État du menu
    # ------------------------------------------------------------------ #
    @property
    def mode(self) -> str:
        return MODE_ORDER[self.mode_index]

    def _refresh_labels(self) -> None:
        mode = C.GAME_MODES[self.mode]
        self.buttons.buttons[0].label = f"Mode : {mode['label']}"
        self.buttons.buttons[0].description = mode["description"]

    # ------------------------------------------------------------------ #
    # Entrées
    # ------------------------------------------------------------------ #
    def on_key_press(self, key: int, modifiers: int) -> None:
        if key in (arcade.key.DOWN, arcade.key.S):
            self._move_selection(1)
        elif key in (arcade.key.UP, arcade.key.Z):
            self._move_selection(-1)
        elif key in (arcade.key.LEFT, arcade.key.Q) and self.buttons.selected == 0:
            self._cycle_mode(-1)
            self.audio.play("ui_hover")
        elif key in (arcade.key.RIGHT, arcade.key.D) and self.buttons.selected == 0:
            self._cycle_mode(1)
            self.audio.play("ui_hover")
        elif key == arcade.key.N:
            self._toggle_mute()
        elif key in (arcade.key.ENTER, arcade.key.NUM_ENTER, arcade.key.SPACE):
            self._activate(self.buttons.selected)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        vec = self.camera.unproject((x, y))
        x, y = vec.x, vec.y
        previous = self.buttons.selected
        self.buttons.on_mouse_motion(x, y)
        self._play_hover(previous)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        vec = self.camera.unproject((x, y))
        x, y = vec.x, vec.y
        if self.buttons.on_mouse_press(x, y) is not None:
            self._activate(self.buttons.selected)

    def _move_selection(self, step: int) -> None:
        previous = self.buttons.selected
        self.buttons.move(step)
        self._play_hover(previous)

    def _play_hover(self, previous: int) -> None:
        """
        Son de survol, et seulement s'il se passe quelque chose.

        Sans cette comparaison, le moindre mouvement de souris sur un bouton
        deja selectionne relancerait le son a chaque pixel parcouru.
        """
        if self.buttons.selected != previous:
            self.audio.play("ui_hover")

    def _cycle_mode(self, step: int) -> None:
        # Pas de son ici : ce serait le deuxieme, par-dessus le clic, quand on
        # change de mode avec Entree.
        self.mode_index = (self.mode_index + step) % len(MODE_ORDER)
        self._refresh_labels()

    def _toggle_mute(self) -> None:
        """Coupe-son (touche N), le meme que dans le jeu."""
        if not self.audio.toggle_mute():
            self.audio.start_menu_music()

    def _activate(self, index: int) -> None:
        self.audio.play("ui_click")
        if index == 0:
            self._cycle_mode(1)
        elif index == 1:
            self._start_game()
        elif index == 2:
            arcade.close_window()

    def _start_game(self) -> None:
        from src.views.game_view import GameView

        self.audio.stop_all()
        game = GameView(mode=self.mode)
        game.setup()
        self.window.show_view(game)

    # ------------------------------------------------------------------ #
    # Rendu
    # ------------------------------------------------------------------ #
    def on_draw(self) -> None:
        self.clear()
        with self.camera.activate():
            draw_logo(C.WINDOW_WIDTH / 2, LOGO_CENTER_Y, LOGO_MAX_WIDTH, LOGO_MAX_HEIGHT)
            self._draw_lore()
            self.buttons.draw()
            self._draw_mode_marker()
            self._draw_leaderboard()

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        apply_letterbox(self.camera, width, height)

    def _draw_lore(self) -> None:
        top = draw_panel(
            LEFT_X, LORE_BOTTOM, LEFT_WIDTH, PANELS_TOP - LORE_BOTTOM,
            title="MOURIR POUR MIEUX AVANCER",
        )
        draw_text_cached(
            LORE,
            LEFT_X + 18, top - 4, C.COLOR_TEXT, LORE_FONT_SIZE,
            width=int(LEFT_WIDTH - 36), multiline=True,
        )

    def _draw_mode_marker(self) -> None:
        """
        Trois traits sous le bouton de mode : lequel des trois modes est choisi.

        Le libellé dit déjà le mode, mais pas COMBIEN il y en a. Sans ces
        repères, personne ne devine qu'il faut appuyer sur gauche/droite.
        """
        button = self.buttons.buttons[0]
        width = 18
        gap = 6
        total = len(MODE_ORDER) * width + (len(MODE_ORDER) - 1) * gap
        left = button.center_x + button.width / 2 - 20 - total
        y = button.center_y + 4
        for index in range(len(MODE_ORDER)):
            color = C.COLOR_ACCENT if index == self.mode_index else C.COLOR_HUD_BORDER
            arcade.draw_lbwh_rectangle_filled(
                left + index * (width + gap), y, width, 3, color
            )

    def _draw_leaderboard(self) -> None:
        height = PANELS_TOP - PANELS_BOTTOM
        top = draw_panel(
            RIGHT_X, PANELS_BOTTOM, RIGHT_WIDTH, height,
            title="TABLEAU DES SCORES (local)",
        )
        left = RIGHT_X + 18
        width = RIGHT_WIDTH - 36

        if not self.leaderboard:
            draw_text_cached(
                "Aucune partie enregistree.\nLa premiere tentative fera date.",
                left, top - 4, C.COLOR_TEXT_DIM, 14,
                width=int(width), multiline=True,
            )
            return

        rows = []
        row_colors = []
        for run in self.leaderboard[:SCORE_ROWS_MAX]:
            minutes, seconds = divmod(int(run.get("elapsed", 0)), 60)
            victory = bool(run.get("victory"))
            rows.append(
                (
                    "VICTOIRE" if victory else "echec",
                    f"{minutes:02d}:{seconds:02d}",
                    str(run.get("deaths_total", 0)),
                    str(run.get("deaths_devoured", 0)),
                    str(run.get("torches_placed", 0)),
                    C.GAME_MODES.get(run.get("mode", ""), {}).get("label", "?"),
                )
            )
            row_colors.append(C.COLOR_ACCENT if victory else C.COLOR_TEXT_DIM)

        draw_table(left, top, width, SCORE_COLUMNS, rows,
                   row_height=SCORE_ROW_HEIGHT, font_size=SCORE_FONT_SIZE,
                   row_colors=row_colors)
