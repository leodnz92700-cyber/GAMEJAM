"""
Fichier : text_cache.py
Auteur : base technique (game jam)

Description :
Petit cache d'objets `arcade.Text`.

Arcade avertit (à juste titre) que `arcade.draw_text` est très lent : la texture
du texte est reconstruite à chaque appel, et le HUD en affiche une dizaine par
frame. `draw_text_cached` garde le même confort d'écriture qu'un appel direct,
mais réutilise l'objet `Text` créé à la première frame et ne met à jour que la
chaîne de caractères.

Utilisation identique à `arcade.draw_text` :

    draw_text_cached("Etage 1", 20, 40, C.COLOR_TEXT, 14, anchor_x="center")

Pour tout texte affiché PAR-DESSUS le jeu, préférez `draw_text_shadowed` : sans
ombre portée, un texte clair devient illisible sur une zone éclairée.

C'est aussi ici qu'est appliquée la **police pixel du jeu** (`src/ui/fonts.py`) :
tout texte qui passe par ce module la reçoit automatiquement, il n'y a rien à
préciser à l'appel. Un appel peut toujours imposer sa propre `font_name`.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.ui.fonts import ui_font

_CACHE: dict[tuple, arcade.Text] = {}


def draw_text_cached(text, x: float, y: float, color=(255, 255, 255, 255),
                     font_size: float = 12, **kwargs) -> arcade.Text:
    """Dessine un texte en réutilisant l'objet `Text` associé à cet emplacement."""
    # La police pixel s'applique a tout le monde, sauf si l'appelant en impose
    # une autre. `ui_font()` charge le fichier au premier appel, puis se contente
    # de renvoyer le nom deja connu.
    kwargs.setdefault("font_name", ui_font())
    key = (
        round(x, 1),
        round(y, 1),
        font_size,
        tuple(color),
        tuple(sorted((name, str(value)) for name, value in kwargs.items())),
    )
    text_object = _CACHE.get(key)
    if text_object is None:
        text_object = arcade.Text(str(text), x, y, color, font_size, **kwargs)
        _CACHE[key] = text_object
    elif text_object.text != str(text):
        text_object.text = str(text)
    text_object.draw()
    return text_object


def draw_text_shadowed(text, x: float, y: float, color=(255, 255, 255, 255),
                       font_size: float = 12, **kwargs) -> arcade.Text:
    """
    Comme `draw_text_cached`, mais avec une ombre portée d'un pixel.

    L'ATH est dessiné en transparence par-dessus le jeu : sans ombre, le texte
    devient illisible dès qu'il passe au-dessus d'une zone éclairée par une
    torche. C'est la version à utiliser pour tout ce qui est affiché en jeu.
    """
    draw_text_cached(text, x + 1, y - 1, C.COLOR_TEXT_SHADOW, font_size, **kwargs)
    return draw_text_cached(text, x, y, color, font_size, **kwargs)


def clear_cache() -> None:
    """Vide le cache (utile si vous changez de resolution en cours d'execution)."""
    _CACHE.clear()
