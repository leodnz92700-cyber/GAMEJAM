"""
Fichier : key_icons.py
Auteur : base technique (game jam)

Description :
Petites touches de clavier dessinées, pour les rappels de commandes de l'ATH.

Tout l'ATH est posé en transparence sur le jeu : une touche dessinée se repère
d'un coup d'oeil là où une ligne de texte se perdrait dans le décor. Les icônes
sont tracées à la main (rectangle + lettre, ou rectangle + triangle pour les
flèches) plutôt que dessinées dans un fichier : elles restent nettes à toutes
les tailles et ne dépendent d'aucun asset.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached

# Sommets d'un triangle de flèche, en fraction de la taille de la touche.
ARROW_SHAPES = {
    "up": ((0.0, 0.26), (-0.24, -0.14), (0.24, -0.14)),
    "down": ((0.0, -0.26), (-0.24, 0.14), (0.24, 0.14)),
    "left": ((-0.26, 0.0), (0.14, 0.24), (0.14, -0.24)),
    "right": ((0.26, 0.0), (-0.14, 0.24), (-0.14, -0.24)),
}


def draw_keycap(center_x: float, center_y: float, label: str = "",
                arrow: str | None = None, size: float = C.UI_KEYCAP_SIZE,
                alpha: int = 255) -> None:
    """
    Dessine une touche de clavier : un carré bordé, avec une lettre ou une flèche.

    `alpha` sert à griser une touche dont l'action n'est pas disponible (pas de
    fiole en poche, par exemple) sans la faire disparaître de l'interface.
    """
    left = center_x - size / 2
    bottom = center_y - size / 2
    fill = C.COLOR_KEYCAP_FILL
    arcade.draw_lbwh_rectangle_filled(
        left, bottom, size, size, (*fill[:3], int(fill[3] * alpha / 255))
    )
    arcade.draw_lbwh_rectangle_outline(
        left, bottom, size, size, (*C.COLOR_KEYCAP_BORDER, alpha), 1
    )

    if arrow:
        points = ARROW_SHAPES[arrow]
        arcade.draw_triangle_filled(
            *[
                coordinate
                for point in points
                for coordinate in (center_x + point[0] * size, center_y + point[1] * size)
            ],
            (*C.COLOR_KEYCAP_LABEL, alpha),
        )
    elif label:
        draw_text_cached(
            label,
            center_x,
            center_y - size * 0.28,
            (*C.COLOR_KEYCAP_LABEL, alpha),
            size * 0.55,
            anchor_x="center",
            bold=True,
        )


def arrow_cluster_size(size: float, gap: float = 2.0) -> tuple[float, float]:
    """
    Encombrement du bloc de quatre flèches, en pixels.

    Plus utilisé par l'ATH (le déplacement ne se rappelle pas : ZQSD est un
    réflexe acquis), gardé pour un futur écran de commandes ou un tutoriel.
    """
    return size * 3 + gap * 2, size * 2 + gap


def draw_arrow_cluster(left: float, bottom: float, size: float = 16.0,
                       gap: float = 2.0, alpha: int = 255) -> None:
    """
    Dessine le bloc classique des quatre flèches, en T inversé.

    `left` et `bottom` sont le coin bas-gauche du bloc entier.
    """
    step = size + gap
    center_x = left + step + size / 2       # colonne du milieu
    draw_keycap(center_x, bottom + step + size / 2, arrow="up", size=size, alpha=alpha)
    draw_keycap(left + size / 2, bottom + size / 2, arrow="left", size=size, alpha=alpha)
    draw_keycap(center_x, bottom + size / 2, arrow="down", size=size, alpha=alpha)
    draw_keycap(left + 2 * step + size / 2, bottom + size / 2, arrow="right",
                size=size, alpha=alpha)
