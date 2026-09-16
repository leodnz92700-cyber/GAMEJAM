"""
Fichier : logo.py
Auteur : base technique (game jam)

Description :
Chargement et affichage du logo du jeu (`assets/ui/logo.png`).

Trois choses que ce module règle une fois pour toutes :

1. **Le fichier peut manquer.** Un coéquipier qui vient de cloner le dépôt, ou
   un outil qui tourne sans les assets, ne doit pas voir le jeu planter sur
   l'écran d'accueil : on retombe alors sur le titre écrit en toutes lettres.
2. **Le logo est livré sur un fond NOIR OPAQUE, pas sur du transparent**, avec
   une large marge autour du dessin. Posé tel quel, il dessinerait un rectangle
   noir franc par-dessus le fond de l'écran — visible, et impossible à aligner
   puisque le dessin flotte au milieu du vide. On lui fabrique donc un canal
   alpha à partir de sa luminosité (le noir devient transparent, la lueur
   s'estompe toute seule, exactement comme un halo se compose), puis on rogne
   au plus près du dessin. Après rognage, le rectangle rendu EST le dessin.
   La version actuelle du logo est, elle, correctement détourée : le code la
   laisse telle quelle et se contente de la rogner.
3. **Il ne doit jamais être déformé.** `draw_logo` inscrit l'image dans la boîte
   qu'on lui donne en conservant ses proportions, et ne l'agrandit jamais
   au-delà de sa taille d'origine (du pixel art étiré est illisible).
"""
from __future__ import annotations

import arcade
import PIL.Image
import PIL.ImageChops

from src import constants as C
from src.ui.text_cache import draw_text_cached

# Chargé à la première frame de l'écran d'accueil, puis gardé.
# `False` = on a déjà cherché le fichier et il n'existe pas : inutile de
# retenter (et d'imprimer l'avertissement) à chaque frame.
_LOGO: arcade.Texture | None | bool = False


def get_logo() -> arcade.Texture | None:
    """Renvoie la texture du logo, rognée, ou None si l'image est absente."""
    global _LOGO
    if _LOGO is not False:
        return _LOGO

    _LOGO = None
    if C.LOGO_PATH.exists():
        try:
            image = PIL.Image.open(C.LOGO_PATH).convert("RGBA")
            image = _crop_to_artwork(_alpha_from_luminance(image))
            _LOGO = arcade.Texture(image)
        except (OSError, ValueError) as error:
            print(f"[logo] {C.LOGO_PATH.name} illisible ({error}), titre en texte.")
    else:
        print(f"[logo] {C.LOGO_PATH} absent, titre affiche en texte.")
    return _LOGO


def _alpha_from_luminance(image: PIL.Image.Image) -> PIL.Image.Image:
    """
    Transforme le fond noir du logo en transparence.

    Ne fait rien si l'image porte déjà un vrai canal alpha (une version future
    du logo pourrait être exportée en PNG transparent) : on ne détruit pas un
    détourage fait à la main.

    Sinon, l'alpha devient la composante la plus claire de chaque pixel. Le noir
    pur disparaît, la lueur s'éteint progressivement sur ses bords, et le
    logo se fond dans le fond de l'écran au lieu d'y poser une plaque noire.
    """
    alpha = image.getchannel("A")
    if alpha.getextrema()[0] < 255:
        return image                    # déjà détouré, on n'y touche pas

    red, green, blue, _ = image.split()
    brightest = PIL.ImageChops.lighter(PIL.ImageChops.lighter(red, green), blue)
    image.putalpha(brightest)
    return image


# En dessous de ce niveau d'alpha, on considère qu'il n'y a rien : c'est du
# bruit de compression sur le noir, pas du dessin.
_CROP_THRESHOLD = 12


def _crop_to_artwork(image: PIL.Image.Image) -> PIL.Image.Image:
    """Rogne l'image au plus près de ce qui est réellement dessiné."""
    mask = image.getchannel("A").point(lambda value: 255 if value > _CROP_THRESHOLD else 0)
    box = mask.getbbox()
    return image.crop(box) if box else image


def draw_logo(center_x: float, center_y: float, max_width: float,
              max_height: float) -> None:
    """
    Dessine le logo centré, inscrit dans la boîte (`max_width` x `max_height`).

    Sans fichier, on écrit le titre : l'écran reste lisible et utilisable.
    """
    texture = get_logo()
    if texture is None:
        draw_text_cached(
            "LABYRINTH OF SHADOW",
            center_x, center_y - 22, C.COLOR_ACCENT, 44,
            anchor_x="center", bold=True,
        )
        return

    # Le plus petit des deux rapports fait entrer l'image en entier ; le `min`
    # avec 1.0 interdit l'agrandissement, qui rendrait le pixel art baveux.
    scale = min(max_width / texture.width, max_height / texture.height, 1.0)
    arcade.draw_texture_rect(
        texture,
        arcade.XYWH(center_x, center_y, texture.width * scale, texture.height * scale),
        pixelated=True,
    )
