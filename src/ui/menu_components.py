"""
Fichier : menu_components.py
Auteur : base technique (game jam)

Description :
Briques d'interface des écrans hors-jeu (accueil, victoire, défaite) : panneau,
tableau à colonnes alignées, bouton, liste de boutons navigable au clavier ET à
la souris, titre et bandeau d'aide.

Trois partis pris, tous tirés du logo du jeu :

- **Aucun angle arrondi, aucun dégradé.** Le jeu est en pixel art : les menus
  sont faits de rectangles nets, de filets d'un pixel et de coins équerrés.
- **L'or (`C.COLOR_ACCENT`) ne sert qu'à ce qui est actif ou important.** Un
  écran où tout brille ne montre plus rien.
- **Les colonnes sont posées à l'abscisse, jamais alignées avec des espaces.**
  La police du système n'est pas à chasse fixe : remplir avec des espaces donne
  des colonnes en escalier. `draw_table` place chaque cellule et l'aligne
  elle-même, c'est ce qui rend les tableaux droits.

Les menus se pilotent entièrement au clavier (fleches + Entree), la souris
n'étant qu'un confort : dans le noir, on ne cherche pas son curseur.
"""
from __future__ import annotations

from dataclasses import dataclass

import arcade

from src import constants as C
from src.ui.text_cache import draw_text_cached

# Marge intérieure d'un panneau : c'est elle qui aligne verticalement le
# contenu de deux panneaux posés côte à côte.
PANEL_PADDING = 18
# Longueur des équerres dessinées dans les coins d'un panneau.
CORNER_LENGTH = 12
# Blanc laissé entre une cellule alignée à droite et la colonne suivante. Sans
# lui, « 12 » et « Sursis » se touchent et on lit « 12Sursis ».
CELL_GUTTER = 18


# --------------------------------------------------------------------------- #
# Panneaux
# --------------------------------------------------------------------------- #
def draw_panel(left: float, bottom: float, width: float, height: float,
               title: str = "", active: bool = False) -> float:
    """
    Dessine un panneau et renvoie l'ordonnée où son contenu peut commencer.

    Renvoyer ce `y` évite que chaque écran recalcule à la main « hauteur du
    panneau moins la marge moins le titre » : deux panneaux de hauteurs
    différentes commencent alors exactement à la même ligne.
    """
    border = C.COLOR_PANEL_BORDER_ACTIVE if active else C.COLOR_HUD_BORDER
    arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, C.COLOR_PANEL_FILL)
    arcade.draw_lbwh_rectangle_outline(left, bottom, width, height, border, 1)
    _draw_corners(left, bottom, width, height)

    content_top = bottom + height - PANEL_PADDING
    if title:
        draw_text_cached(
            title, left + PANEL_PADDING, content_top - 14, C.COLOR_ACCENT, 14,
            bold=True,
        )
        rule_y = content_top - 24
        arcade.draw_lbwh_rectangle_filled(
            left + PANEL_PADDING, rule_y, width - 2 * PANEL_PADDING, 1, C.COLOR_RULE
        )
        return rule_y - 14
    return content_top


def _draw_corners(left: float, bottom: float, width: float, height: float) -> None:
    """Équerres dorées dans les quatre coins : le cadre d'un grimoire, en pixels."""
    right = left + width
    top = bottom + height
    color = C.COLOR_ACCENT_DIM
    # Deux petits traits par coin : un horizontal, un vertical. Les coins hauts
    # et droits sont decales d'un pixel pour rester DANS le cadre.
    for x in (left, right - CORNER_LENGTH):
        for y in (bottom, top - 1):
            arcade.draw_lbwh_rectangle_filled(x, y, CORNER_LENGTH, 1, color)
    for x in (left, right - 1):
        for y in (bottom, top - CORNER_LENGTH):
            arcade.draw_lbwh_rectangle_filled(x, y, 1, CORNER_LENGTH, color)


# --------------------------------------------------------------------------- #
# Tableaux
# --------------------------------------------------------------------------- #
@dataclass
class Column:
    """Une colonne de tableau : son titre, sa largeur et son alignement."""

    title: str
    width: float
    align: str = "left"      # "left", "right" ou "center"


def draw_table(left: float, top: float, width: float, columns: list[Column],
               rows: list[tuple], row_height: float = 22,
               font_size: float = 13, row_colors: list | None = None) -> float:
    """
    Dessine un tableau à colonnes alignées et renvoie l'ordonnée sous la
    dernière ligne.

    `rows` contient un tuple de chaînes par ligne, de la longueur de `columns`.
    `row_colors` permet de teinter une ligne entière (une victoire en clair, un
    échec en gris) ; à défaut tout est en `C.COLOR_TEXT_DIM`.

    Une ligne sur deux reçoit un fond légèrement plus clair : c'est ce qui
    permet de suivre une ligne du regard jusqu'à la colonne de droite sans
    glisser sur la ligne voisine.
    """
    _draw_table_header(left, top, width, columns, font_size)
    row_top = top - 24

    for index, row in enumerate(rows):
        row_bottom = row_top - (index + 1) * row_height
        if index % 2 == 1:
            arcade.draw_lbwh_rectangle_filled(
                left, row_bottom, width, row_height, C.COLOR_PANEL_FILL_SOFT
            )
        color = row_colors[index] if row_colors else C.COLOR_TEXT_DIM
        _draw_cells(left, row_bottom + row_height / 2 - font_size * 0.42,
                    columns, row, color, font_size)
    return row_top - len(rows) * row_height


def _draw_table_header(left: float, top: float, width: float,
                       columns: list[Column], font_size: float) -> None:
    _draw_cells(left, top - 12, columns,
                [column.title.upper() for column in columns],
                C.COLOR_ACCENT_DIM, font_size - 1)
    arcade.draw_lbwh_rectangle_filled(left, top - 20, width, 1, C.COLOR_RULE)


def _draw_cells(left: float, y: float, columns: list[Column], values,
                color, font_size: float) -> None:
    """Pose chaque cellule à l'abscisse de sa colonne, selon son alignement."""
    x = left
    for column, value in zip(columns, values):
        if column.align == "right":
            anchor_x, cell_x = "right", x + column.width - CELL_GUTTER
        elif column.align == "center":
            anchor_x, cell_x = "center", x + column.width / 2
        else:
            anchor_x, cell_x = "left", x
        draw_text_cached(value, cell_x, y, color, font_size, anchor_x=anchor_x)
        x += column.width


def draw_stat_rows(left: float, top: float, width: float,
                   lines: list[tuple[str, str]], row_height: float = 25,
                   font_size: float = 15) -> float:
    """
    Tableau « libellé … valeur » des écrans de fin, et son ordonnée de sortie.

    Les valeurs sont toutes alignées sur le bord droit, et des points de
    conduite relient le libellé à sa valeur : sans eux, l'oeil perd la ligne
    entre un libellé court et un chiffre à l'autre bout du panneau.

    Un libellé commençant par deux espaces est un DÉTAIL de la ligne précédente
    (« dont pieges ») : il est rentré, plus petit et plus sombre. C'est la
    convention de `RunStats.as_lines`, on la lit ici plutôt que d'imposer une
    autre structure au module de score.
    """
    right = left + width
    y = top
    for label, value in lines:
        detail = label.startswith("  ")
        text = label.strip()
        size = font_size - 2 if detail else font_size
        label_color = C.COLOR_TEXT_DIM if detail else C.COLOR_TEXT
        value_color = C.COLOR_TEXT_DIM if detail else C.COLOR_ACCENT
        label_x = left + (18 if detail else 0)

        if detail:
            # Petit tiret d'arborescence, pour rattacher le detail a sa ligne.
            arcade.draw_lbwh_rectangle_filled(left + 6, y + size * 0.35, 6, 1,
                                              C.COLOR_RULE)
        label_object = draw_text_cached(text, label_x, y, label_color, size)
        value_object = draw_text_cached(value, right, y, value_color, size,
                                        anchor_x="right", bold=not detail)
        _draw_leader(
            label_x + label_object.content_width + 8,
            right - value_object.content_width - 8,
            y + size * 0.35,
        )
        y -= row_height
    return y


def _draw_leader(start_x: float, end_x: float, y: float) -> None:
    """Points de conduite entre un libellé et sa valeur."""
    x = start_x
    while x < end_x - 2:
        arcade.draw_lbwh_rectangle_filled(x, y, 2, 1, C.COLOR_RULE)
        x += 7


# --------------------------------------------------------------------------- #
# Boutons
# --------------------------------------------------------------------------- #
class Button:
    """Un bouton rectangulaire avec un libellé et une description optionnelle."""

    def __init__(self, label: str, x: float, y: float, width: float = 520,
                 height: float = 52, description: str = "", value=None):
        self.label = label
        self.description = description
        self.value = value
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height

    def contains(self, x: float, y: float) -> bool:
        return (
            abs(x - self.center_x) <= self.width / 2
            and abs(y - self.center_y) <= self.height / 2
        )

    def draw(self, selected: bool) -> None:
        """
        Le bouton sélectionné se repère à TROIS signes, pas à un seul : fond plus
        clair, bord doré, et une barre pleine collée à son bord gauche. Sur un
        écran aussi sombre, une simple nuance de bord ne se voit pas.
        """
        left = self.center_x - self.width / 2
        bottom = self.center_y - self.height / 2
        fill = (38, 29, 20) if selected else C.COLOR_PANEL_FILL
        border = C.COLOR_PANEL_BORDER_ACTIVE if selected else C.COLOR_HUD_BORDER

        arcade.draw_lbwh_rectangle_filled(left, bottom, self.width, self.height, fill)
        arcade.draw_lbwh_rectangle_outline(
            left, bottom, self.width, self.height, border, 1
        )
        if selected:
            arcade.draw_lbwh_rectangle_filled(left, bottom, 3, self.height,
                                              C.COLOR_ACCENT)

        # Les deux lignes sont posées par rapport au CENTRE du bouton : elles
        # restent centrées quelle que soit sa hauteur, avec ou sans description.
        # Les décalages laissent le même blanc au-dessus du libellé qu'en dessous
        # des jambages de la description — sans quoi celle-ci touchait le bord
        # bas du bouton et se faisait rogner.
        text_x = left + 20
        has_description = bool(self.description)
        label_y = self.center_y + (2 if has_description else -6)
        draw_text_cached(
            self.label, text_x, label_y,
            C.COLOR_TEXT if selected else C.COLOR_TEXT_DIM, 17,
        )
        if has_description:
            draw_text_cached(
                self.description, text_x, label_y - 17,
                C.COLOR_TEXT_DIM if selected else C.COLOR_TEXT_FAINT, 12,
            )


class ButtonList:
    """Liste verticale de boutons avec un curseur de sélection."""

    def __init__(self, buttons: list[Button]):
        self.buttons = buttons
        self.selected = 0

    @property
    def current(self) -> Button:
        return self.buttons[self.selected]

    def move(self, step: int) -> None:
        if not self.buttons:
            return
        self.selected = (self.selected + step) % len(self.buttons)

    def on_mouse_motion(self, x: float, y: float) -> None:
        for index, button in enumerate(self.buttons):
            if button.contains(x, y):
                self.selected = index
                return

    def on_mouse_press(self, x: float, y: float) -> Button | None:
        for index, button in enumerate(self.buttons):
            if button.contains(x, y):
                self.selected = index
                return button
        return None

    def draw(self) -> None:
        for index, button in enumerate(self.buttons):
            button.draw(index == self.selected)


# --------------------------------------------------------------------------- #
# Titres et bandeau d'aide
# --------------------------------------------------------------------------- #
def draw_title(text: str, y: float, size: int = 44,
               color=C.COLOR_ACCENT) -> None:
    """Titre centré, souligné d'un filet court : la marque des écrans de fin."""
    draw_text_cached(
        text, C.WINDOW_WIDTH / 2, y, color, size, anchor_x="center", bold=True,
    )
    # Le filet se place SOUS les jambages, donc a une distance proportionnelle a
    # la taille du titre : a 14 px fixes, il barrait un titre de 44 px.
    arcade.draw_lbwh_rectangle_filled(
        C.WINDOW_WIDTH / 2 - 60, y - size * 0.42, 120, 1, C.COLOR_ACCENT_DIM
    )


def draw_subtitle(text: str, y: float, color=C.COLOR_TEXT_DIM,
                  size: int = 16) -> None:
    """Ligne d'accroche sous un titre ou un logo."""
    draw_text_cached(
        text, C.WINDOW_WIDTH / 2, y, color, size, anchor_x="center", italic=True,
    )


def draw_hint(text: str, y: float = 22) -> None:
    """Rappel des touches, en bas de l'écran, séparé du contenu par un filet."""
    arcade.draw_lbwh_rectangle_filled(
        C.WINDOW_WIDTH / 2 - 260, y + 22, 520, 1, C.COLOR_RULE
    )
    draw_text_cached(
        text, C.WINDOW_WIDTH / 2, y, C.COLOR_TEXT_DIM, 13, anchor_x="center",
    )
