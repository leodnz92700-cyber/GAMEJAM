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
"""
from __future__ import annotations

import arcade

_CACHE: dict[tuple, arcade.Text] = {}


def draw_text_cached(text, x: float, y: float, color=(255, 255, 255, 255),
                     font_size: float = 12, **kwargs) -> arcade.Text:
    """Dessine un texte en réutilisant l'objet `Text` associé à cet emplacement."""
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


def clear_cache() -> None:
    """Vide le cache (utile si vous changez de resolution en cours d'execution)."""
    _CACHE.clear()
