"""
Fichier : end_screen.py
Auteur : base technique (game jam)

Description :
Mise en page commune aux deux écrans de fin (victoire et défaite).

Les deux écrans disent la même chose — voici ta partie, voici tes morts — et
seuls le titre, sa couleur et la phrase de verdict changent. Les écrire deux
fois, c'était garantir qu'ils finiraient désalignés l'un par rapport à l'autre :
tout est donc posé ici, une seule fois, sur une grille fixe.

Le bas de l'écran porte **la balance des morts** : combien ont été choisies,
combien ont été subies, et la barre qui compare les deux. C'est la lecture la
plus parlante du thème « mourir pour mieux avancer » — un joueur qui gagne avec
huit morts choisies et zéro dévoration a joué le jeu ; l'inverse l'a subi.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.menu_components import (
    draw_hint,
    draw_panel,
    draw_stat_rows,
    draw_subtitle,
    draw_title,
)
from src.ui.text_cache import draw_text_cached

# --- La grille de l'écran de fin -------------------------------------------- #
TITLE_Y = 636
TITLE_SIZE = 38            # la police pixel a des capitales tres pleines
VERDICT_Y = 594

PANEL_WIDTH = 640
PANEL_LEFT = (C.WINDOW_WIDTH - PANEL_WIDTH) / 2

STATS_BOTTOM = 226
STATS_HEIGHT = 330
STAT_ROW_HEIGHT = 27

BALANCE_BOTTOM = 88
BALANCE_HEIGHT = 122
BAR_HEIGHT = 12


def draw_end_screen(title: str, title_color, verdict: str, verdict_color,
                    stats) -> None:
    """Dessine un écran de fin complet à partir des statistiques de la partie."""
    draw_title(title, TITLE_Y, TITLE_SIZE, color=title_color)
    if verdict:
        draw_subtitle(verdict, VERDICT_Y, color=verdict_color, size=17)

    top = draw_panel(
        PANEL_LEFT, STATS_BOTTOM, PANEL_WIDTH, STATS_HEIGHT, title="TA PARTIE"
    )
    draw_stat_rows(
        PANEL_LEFT + 18, top, PANEL_WIDTH - 36, stats.as_lines(),
        row_height=STAT_ROW_HEIGHT,
    )

    _draw_balance(stats)
    draw_hint("Entree : retour a l'ecran d'accueil")


def _draw_balance(stats) -> None:
    """Barre comparant les morts choisies aux morts subies."""
    draw_panel(
        PANEL_LEFT, BALANCE_BOTTOM, PANEL_WIDTH, BALANCE_HEIGHT,
        title="LE COMPTE DE TES MORTS",
    )
    chosen = stats.deaths_by_vial + stats.deaths_by_trap
    suffered = stats.deaths_devoured

    left = PANEL_LEFT + 18
    width = PANEL_WIDTH - 36
    right = left + width

    draw_text_cached(f"{chosen} choisies", left, 130, C.COLOR_ACCENT, 15, bold=True)
    draw_text_cached(f"{suffered} subies", right, 130, C.COLOR_DANGER, 15,
                     anchor_x="right", bold=True)

    bar_y = BALANCE_BOTTOM + 16
    total = chosen + suffered
    if total == 0:
        # Aucune mort : ni barre doree ni barre rouge, juste le rail vide. Un
        # partage 50/50 laisserait croire a une devoration qui n'a pas eu lieu.
        arcade.draw_lbwh_rectangle_filled(left, bar_y, width, BAR_HEIGHT,
                                          C.COLOR_PANEL_FILL_SOFT)
    else:
        chosen_width = width * chosen / total
        arcade.draw_lbwh_rectangle_filled(left, bar_y, chosen_width, BAR_HEIGHT,
                                          C.COLOR_ACCENT)
        arcade.draw_lbwh_rectangle_filled(left + chosen_width, bar_y,
                                          width - chosen_width, BAR_HEIGHT,
                                          C.COLOR_DANGER)
    arcade.draw_lbwh_rectangle_outline(left, bar_y, width, BAR_HEIGHT,
                                       C.COLOR_HUD_BORDER, 1)
