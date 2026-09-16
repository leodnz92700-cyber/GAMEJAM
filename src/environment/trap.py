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
  - `SkeletonArcher` : un squelette planté dans une grande salle, qui décoche
    ses flèches en travers de la pièce. On ne peut ni le tuer ni le pousser : il
    fait partie du décor, exactement comme un piège. Sa cadence est infernale,
    la fenêtre entre deux flèches ne suffit pas à traverser la ligne de tir :
    la première traversée se paie d'une mort, et c'est voulu. Le CADAVRE laissé
    sur la trajectoire arrête les flèches — le joueur se fabrique un bouclier
    avec son ancien corps, et l'archer continue de tirer dessus indéfiniment.

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


class Arrow(arcade.Sprite):
    """Flèche décochée par un `SkeletonArcher`."""

    def __init__(self, center_x: float, center_y: float,
                 direction: tuple[float, float], speed: float):
        # La flèche du pack est dessinée pointe à droite : on la fait tourner
        # dans son sens de vol. Sa boîte de collision reste minuscule, sinon on
        # mourrait en la frôlant.
        super().__init__(
            load_single("arrow.png", tuple(centered_box(*C.ARROW_HIT_BOX))),
            center_x=center_x,
            center_y=center_y,
        )
        self.direction = direction
        self.speed = speed
        self.lifetime = 0.0
        self.travelled = 0.0        # distance parcourue : la flèche a une portée
        self.angle = {
            (1.0, 0.0): 0, (-1.0, 0.0): 180, (0.0, 1.0): -90, (0.0, -1.0): 90
        }.get(direction, 0)

    def advance(self, delta_time: float) -> None:
        step = self.speed * delta_time
        self.center_x += self.direction[0] * step
        self.center_y += self.direction[1] * step
        self.travelled += step
        self.lifetime += delta_time

    @property
    def spent(self) -> bool:
        """
        La flèche a fini sa course.

        Sans portée, un tir qui sort par une ouverture traverserait tout l'étage
        et tuerait le joueur trois salles plus loin, sans qu'il ait jamais vu
        l'archer : une mort incompréhensible, donc injuste. Le danger doit rester
        dans la salle du tireur.
        """
        return self.travelled > C.ARROW_RANGE or self.lifetime > C.ARROW_LIFETIME


class SkeletonArcher(arcade.Sprite):
    """
    Squelette archer : un tireur immobile et indestructible.

    Il n'a ni vie ni intelligence : c'est un piège qui a une silhouette. Il tire
    toujours dans la même direction, sans jamais s'arrêter — même une fois le
    joueur tué, même quand un cadavre encaisse toutes ses flèches. C'est ce qui
    rend le cadavre-bouclier durable : le danger ne disparaît pas, il est
    seulement absorbé.
    """

    def __init__(self, center_x: float, center_y: float, direction: str = "down",
                 interval: float = C.ARCHER_DEFAULT_INTERVAL,
                 speed: float = C.ARCHER_DEFAULT_SPEED):
        self.direction_name = direction if direction in DIRECTION_VECTORS else "down"
        self.direction = DIRECTION_VECTORS[self.direction_name]
        self.idle_frames, self.shoot_frames = self._load_animations(self.direction_name)
        # Le squelette fait 32x48 comme le héros : même boîte, même remontée du
        # dessin pour que ses pieds se posent au bord du couloir.
        super().__init__(self.idle_frames[0], center_x=center_x, center_y=center_y)

        self.interval = interval
        self.speed = speed
        # Décalage initial pour que deux archers d'une même salle ne tirent pas
        # exactement ensemble, et que le joueur n'arrive pas toujours sur le
        # même temps du cycle.
        self.cooldown = interval * 0.5
        self.shoot_timer = 0.0        # > 0 : animation de tir en cours
        self._arrow_released = True   # la flèche de ce tir est-elle déjà partie ?
        self.shots_fired = 0          # jamais remis à zéro : l'archer ne s'arrête pas

    @staticmethod
    def _load_animations(direction_name: str):
        """Bandes du pack, orientées dans le sens de tir (la gauche est un miroir)."""
        side = direction_name in ("left", "right")
        suffix = "side" if side else direction_name
        flipped = direction_name == "left"
        frame_width, frame_height = C.ARCHER_FRAME_SIZE
        # Même boîte et même remontée que le héros : l'archer est solide (on ne
        # le traverse pas pour esquiver ses flèches) et ses pieds ne doivent pas
        # mordre sur la tuile du dessous. Voir `PLAYER_ART_LIFT`.
        box = tuple(centered_box(*C.PLAYER_HIT_BOX))
        idle = load_strip(
            f"archer_idle_{suffix}.png", frame_width, frame_height,
            box, flipped=flipped, lift=C.PLAYER_ART_LIFT,
        )
        shoot = load_strip(
            f"archer_shoot_{suffix}.png", frame_width, frame_height,
            box, flipped=flipped, lift=C.PLAYER_ART_LIFT,
        )
        return idle, shoot

    @property
    def muzzle(self) -> tuple[float, float]:
        """Point de départ de la flèche : juste devant l'archer, à hauteur d'arc."""
        return (
            self.center_x + self.direction[0] * (C.TILE_SIZE / 2 + 8),
            self.center_y + self.direction[1] * (C.TILE_SIZE / 2 + 8),
        )

    def update_emitter(self, delta_time: float, arrow_list: arcade.SpriteList) -> Arrow | None:
        """
        Fait vivre l'archer : cadence, animation, et départ de la flèche.

        La cadence (`interval`) court en CONTINU, indépendamment de l'animation :
        c'est elle, et elle seule, qui donne le rythme que le joueur doit
        apprendre. La flèche part à l'image où l'arc se détend
        (`ARCHER_RELEASE_FRAME`), donc un peu après le début du geste : le tir se
        voit venir, ce qui rend le rythme lisible même dans le noir.
        """
        arrow = None

        self.cooldown -= delta_time
        if self.cooldown <= 0:
            self.cooldown += self.interval
            self.shoot_timer = C.ARCHER_SHOOT_ANIMATION
            self._arrow_released = False

        if self.shoot_timer <= 0:
            self.texture = self.idle_frames[0]
            return None

        self.shoot_timer = max(0.0, self.shoot_timer - delta_time)
        progress = 1.0 - self.shoot_timer / C.ARCHER_SHOOT_ANIMATION
        index = min(len(self.shoot_frames) - 1, int(progress * len(self.shoot_frames)))
        self.texture = self.shoot_frames[index]

        if not self._arrow_released and index >= C.ARCHER_RELEASE_FRAME:
            self._arrow_released = True
            self.shots_fired += 1
            arrow = Arrow(*self.muzzle, direction=self.direction, speed=self.speed)
            arrow_list.append(arrow)
        return arrow


def make_trap_from_map_object(map_object):
    """Construit le bon type de piège à partir d'un objet Tiled."""
    properties = map_object.properties
    # "dart" reste accepté : c'est le nom historique du piège dans les cartes
    # déjà dessinées, et il désigne aujourd'hui le squelette archer.
    if map_object.type in ("archer", "dart", "skeleton"):
        return SkeletonArcher(
            center_x=map_object.center_x,
            center_y=map_object.center_y,
            direction=str(properties.get("direction", "down")),
            interval=float(properties.get("interval", C.ARCHER_DEFAULT_INTERVAL)),
            speed=float(properties.get("speed", C.ARCHER_DEFAULT_SPEED)),
        )
    return SpikeTrap(center_x=map_object.center_x, center_y=map_object.center_y)
