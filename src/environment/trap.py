"""
Fichier : trap.py
Auteur : base technique (game jam)

Description :
Les pièges du labyrinthe. Un piège est toujours à double tranchant : il tue le
joueur qui ne l'a pas vu venir, mais il est aussi le moyen de mourir
volontairement quand la fiole a déjà servi.

Deux pièges pour l'instant :
  - `SpikeTrap` : visible en permanence, et il BAT EN CONTINU. Les pointes
    jaillissent puis retombent : le joueur voit le danger et doit l'esquiver en
    lisant le rythme. Il barre toute la largeur du couloir, donc il ne doit
    jamais rester mortel en permanence — ce serait un cul-de-sac définitif.
    Et quand le joueur veut mourir pour laisser son corps à cet endroit, il lui
    suffit d'attendre les pointes.
  - `DartTrap` : grille percée dans un mur qui tire des projectiles à intervalle
    régulier en travers d'un couloir. Un cadavre posé sur la trajectoire ARRÊTE
    les projectiles — le joueur se fabrique un bouclier avec son ancien corps.

Un piège occupe exactement une tuile. Pour barrer un couloir de deux tuiles,
posez deux pièges côte à côte dans Tiled.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.textures import centered_box, load_single, load_strip

DIRECTION_VECTORS = {
    "up": (0.0, 1.0),
    "down": (0.0, -1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


class SpikeTrap(arcade.Sprite):
    """Piège à pointes, visible en permanence et cyclique."""

    def __init__(self, center_x: float, center_y: float):
        self.frames = load_strip(
            "trap_spike_strip.png", C.TILE_SIZE, C.TILE_SIZE, tuple(centered_box(28, 28))
        )
        super().__init__(self.frames[0], center_x=center_x, center_y=center_y)
        self.frame_index = 0

    @property
    def is_lethal(self) -> bool:
        """Vrai uniquement pendant la fraction du cycle où les pointes sont sorties."""
        return self.frame_index in C.SPIKE_LETHAL_FRAMES

    def update_cycle(self, clock: float) -> None:
        """
        Cale l'animation sur l'horloge du niveau.

        Tous les pièges partagent la même horloge : ceux qui barrent ensemble un
        couloir de deux tuiles jaillissent donc en même temps, sinon il serait
        impossible de traverser.
        """
        phase = clock % C.SPIKE_CYCLE_DURATION
        if phase < C.SPIKE_SAFE_DURATION:
            self.frame_index = 0
        else:
            progress = (phase - C.SPIKE_SAFE_DURATION) / C.SPIKE_STRIKE_DURATION
            self.frame_index = min(
                len(self.frames) - 1, 1 + int(progress * (len(self.frames) - 1))
            )
        self.texture = self.frames[self.frame_index]


class Dart(arcade.Sprite):
    """Projectile tiré par un `DartTrap`."""

    def __init__(self, center_x: float, center_y: float,
                 direction: tuple[float, float], speed: float):
        super().__init__(
            load_single("dart.png", tuple(centered_box(8, 8))),
            center_x=center_x,
            center_y=center_y,
        )
        self.direction = direction
        self.speed = speed
        self.lifetime = 0.0
        # Oriente le projectile dans son sens de tir.
        self.angle = {(1.0, 0.0): 90, (-1.0, 0.0): 270, (0.0, 1.0): 0, (0.0, -1.0): 180}.get(
            direction, 0
        )

    def advance(self, delta_time: float) -> None:
        self.center_x += self.direction[0] * self.speed * delta_time
        self.center_y += self.direction[1] * self.speed * delta_time
        self.lifetime += delta_time


class DartTrap(arcade.Sprite):
    """Émetteur de projectiles, encastré dans un mur et tirant en travers du couloir."""

    def __init__(self, center_x: float, center_y: float, direction: str = "down",
                 interval: float = C.DART_DEFAULT_INTERVAL,
                 speed: float = C.DART_DEFAULT_SPEED):
        super().__init__(
            load_single("trap_dart.png"), center_x=center_x, center_y=center_y
        )
        self.direction = DIRECTION_VECTORS.get(direction, (0.0, -1.0))
        self.interval = interval
        self.speed = speed
        # Décalage initial pour que le joueur ne tombe pas toujours sur un tir
        # au moment exact où il arrive devant.
        self.cooldown = interval * 0.5

    def update_emitter(self, delta_time: float, dart_list: arcade.SpriteList) -> Dart | None:
        """Fait s'écouler le temps et tire si le délai est écoulé."""
        self.cooldown -= delta_time
        if self.cooldown > 0:
            return None
        self.cooldown = self.interval
        dart = Dart(
            center_x=self.center_x + self.direction[0] * (C.TILE_SIZE / 2 + 6),
            center_y=self.center_y + self.direction[1] * (C.TILE_SIZE / 2 + 6),
            direction=self.direction,
            speed=self.speed,
        )
        dart_list.append(dart)
        return dart


def make_trap_from_map_object(map_object):
    """Construit le bon type de piège à partir d'un objet Tiled."""
    properties = map_object.properties
    if map_object.type == "dart":
        return DartTrap(
            center_x=map_object.center_x,
            center_y=map_object.center_y,
            direction=str(properties.get("direction", "down")),
            interval=float(properties.get("interval", C.DART_DEFAULT_INTERVAL)),
            speed=float(properties.get("speed", C.DART_DEFAULT_SPEED)),
        )
    return SpikeTrap(center_x=map_object.center_x, center_y=map_object.center_y)
