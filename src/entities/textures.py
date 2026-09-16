"""
Fichier : textures.py
Auteur : base technique (game jam)

Description :
Chargement et découpage des feuilles de sprites du pack graphique.

Deux besoins que ce module couvre :

  1. **Découper les bandes d'animation.** Les sprites du pack sont livrés en
     bandes horizontales (le héros qui court = 6 images de 32x48 côte à côte).
     `load_strip` renvoie la liste des textures, avec un cache : une bande n'est
     lue qu'une fois même si dix entités s'en servent.

  2. **Corriger les boîtes de collision.** Par défaut, Arcade prend toute
     l'image comme boîte de collision. Le héros fait 32x48 alors que les
     couloirs les plus étroits font 32 px de large : il resterait coincé en
     permanence. On lui donne donc une petite boîte au niveau des pieds, ce qui
     est de toute façon la convention en vue de dessus.

Les coordonnées d'une boîte de collision sont relatives au CENTRE de la texture,
axe Y vers le haut.
"""
from __future__ import annotations

from functools import lru_cache

import arcade
from PIL import Image

from src import constants as C


def feet_box(texture_width: int, texture_height: int,
             box_width: int, box_height: int) -> list[tuple[float, float]]:
    """
    Boîte de collision rectangulaire posée au BAS de la texture.

    Réservée aux décors dont la base seule est solide (l'escalier de sortie, par
    exemple). NE PAS l'utiliser pour un personnage qui se déplace : la boîte
    serait décalée sous le centre du sprite, et le personnage ne pourrait plus
    tenir dans un couloir d'une seule tuile (sa boîte mordrait le mur du bas).
    Pour les personnages, voir `centered_box`.
    """
    half_width = box_width / 2
    bottom = -texture_height / 2
    top = bottom + box_height
    return [(-half_width, bottom), (half_width, bottom), (half_width, top), (-half_width, top)]


def centered_box(box_width: int, box_height: int) -> list[tuple[float, float]]:
    """
    Boîte de collision rectangulaire centrée sur la texture.

    C'est la boîte des personnages : le sprite du héros fait 32x48 alors que les
    couloirs les plus étroits font 32 px, donc sa tête et ses pieds débordent
    volontairement sur les murs du haut et du bas. Seul un petit rectangle
    central se cogne.
    """
    half_width = box_width / 2
    half_height = box_height / 2
    return [
        (-half_width, -half_height),
        (half_width, -half_height),
        (half_width, half_height),
        (-half_width, half_height),
    ]


@lru_cache(maxsize=64)
def _load_image(name: str) -> Image.Image:
    return Image.open(C.SPRITES_DIR / name).convert("RGBA")


def lift_art(frame: Image.Image, lift: int) -> Image.Image:
    """
    Remonte le dessin au-dessus de son point de collision.

    Arcade dessine une texture centrée sur la position du sprite. En ajoutant
    `2 * lift` lignes transparentes SOUS l'image, on décale le centre vers le
    bas : le personnage apparaît donc plus haut que son point de collision. Ses
    pieds se posent au bord du couloir au lieu de s'enfoncer dans le mur d'en
    bas, et c'est sa tête qui déborde sur le mur du haut — ce qui se lit
    correctement, puisqu'il est dessiné par-dessus.
    """
    if lift <= 0:
        return frame
    canvas = Image.new("RGBA", (frame.width, frame.height + 2 * lift), (0, 0, 0, 0))
    canvas.paste(frame, (0, 0))
    return canvas


def load_strip(name: str, frame_width: int, frame_height: int,
               hit_box: tuple | None = None, flipped: bool = False,
               lift: int = 0) -> list[arcade.Texture]:
    """
    Découpe une bande horizontale en une liste de textures.

    `hit_box` est un tuple de points (voir `centered_box`), partagé par toutes
    les images de la bande. `flipped` renvoie la bande miroir, pour obtenir la
    marche vers la gauche à partir de la marche vers la droite. `lift` remonte
    le dessin au-dessus du point de collision (voir `lift_art`).
    """
    return _load_strip_cached(name, frame_width, frame_height, hit_box, flipped, lift)


@lru_cache(maxsize=64)
def _load_strip_cached(name, frame_width, frame_height, hit_box, flipped, lift):
    image = _load_image(name)
    count = max(1, image.width // frame_width)
    textures = []
    for index in range(count):
        frame = image.crop(
            (index * frame_width, 0, (index + 1) * frame_width, frame_height)
        )
        if flipped:
            frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
        textures.append(
            arcade.Texture(
                lift_art(frame, lift),
                hit_box_points=list(hit_box) if hit_box else None,
                hash=f"{name}:{index}:{'flip' if flipped else 'normal'}:lift{lift}",
            )
        )
    return textures


def load_single(name: str, hit_box: tuple | None = None) -> arcade.Texture:
    """Charge une image simple, avec une boîte de collision optionnelle."""
    return _load_single_cached(name, hit_box)


@lru_cache(maxsize=64)
def _load_single_cached(name, hit_box):
    image = _load_image(name)
    return arcade.Texture(
        image,
        hit_box_points=list(hit_box) if hit_box else None,
        hash=f"{name}:single:{hit_box}",
    )
