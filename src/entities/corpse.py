"""
Fichier : corpse.py
Auteur : base technique (game jam)

Description :
Le cadavre : la mécanique centrale du jeu.

C'est littéralement le CORPS du joueur qui reste sur place : le sprite du
cadavre est la dernière image de l'animation de mort du héros. La transition
entre « le personnage s'effondre » et « le cadavre est là » est donc invisible,
et le corps qui bloque les fléchettes est bien celui qu'on vient de perdre.

Un cadavre issu d'une mort VOLONTAIRE (fiole ou piège) reste dans le niveau et :
  - émet une faible lueur, ce qui en fait un repère dans le noir ;
  - a une présence physique : il maintient une plaque de pression enfoncée et
    arrête les projectiles, tout en restant franchissable (on marche dessus,
    il ne bouche jamais un couloir).

Les objets que le joueur transportait ne sont PAS rangés dans le cadavre : ils
tombent au sol autour de lui (voir `Level.drop_items`). On les ramasse donc
comme n'importe quel objet, sans avoir à fouiller quoi que ce soit.

Un joueur dévoré par la créature ne laisse AUCUN cadavre : c'est toute la
différence entre choisir sa mort et la subir.
"""
from __future__ import annotations

import math

import arcade

from src import constants as C
from src.entities.textures import centered_box, load_strip


class Corpse(arcade.Sprite):
    """Dépouille persistante laissée par une mort volontaire."""

    def __init__(self, center_x: float, center_y: float, cause: str = C.DEATH_VIAL):
        # Dernière image de l'animation de mort : le corps au sol. Même format
        # que la bande de mort (48x48), pas celui du personnage debout.
        body = load_strip(
            "player_death.png",
            *C.PLAYER_DEATH_FRAME_SIZE,
            tuple(centered_box(*C.CORPSE_HIT_BOX)),
            lift=C.PLAYER_ART_LIFT,
        )[-1]
        super().__init__(body, center_x=center_x, center_y=center_y)

        self.cause = cause
        self.age = 0.0
        # Décalage de phase, pour que les cadavres ne pulsent pas en choeur.
        self._phase = (center_x * 0.013 + center_y * 0.017) % (math.pi * 2)

    def light_intensity(self) -> float:
        """Pulsation lente de la lueur (utilisée par le moteur de lumière)."""
        return 0.85 + 0.15 * math.sin(self.age * 1.6 + self._phase)

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.age += delta_time
