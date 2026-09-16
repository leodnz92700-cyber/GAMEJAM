"""
Fichier : player.py
Auteur : base technique (game jam)

Description :
Le joueur : déplacement au clavier, animation dans quatre directions,
inventaire limité, et actions (interagir, planter une torche, boire la fiole).

Le joueur ne décide PAS de sa propre mort ici : il expose son inventaire, et
c'est `death_manager` qui applique les conséquences (cadavre ou non, objets
conservés ou non). Cela évite d'éparpiller la règle centrale du jeu.

Les sprites viennent du pack Dungeons & Pixels (voir tools/import_pack_assets.py).
La marche vers la gauche est la bande "profil" retournée : le pack ne fournit
que trois directions.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.items import Item
from src.entities.textures import centered_box, load_strip
from src.mechanics.inventory_system import Inventory


def _load_player_textures() -> dict[tuple[str, str], list[arcade.Texture]]:
    """Toutes les animations du héros, indexées par (état, direction)."""
    frame_width, frame_height = C.PLAYER_FRAME_SIZE
    box = tuple(centered_box(*C.PLAYER_HIT_BOX))

    def strip(name: str, flipped: bool = False):
        return load_strip(
            name, frame_width, frame_height, box, flipped, lift=C.PLAYER_ART_LIFT
        )

    return {
        # Une seule bande de mort dans le pack : elle sert quelle que soit la
        # direction regardée au moment de la chute. Elle a son PROPRE format
        # (48x48, un corps allongé est large) : la découper comme les autres
        # coupe chaque pose en deux et fait clignoter l'animation.
        ("death", "any"): load_strip(
            "player_death.png",
            *C.PLAYER_DEATH_FRAME_SIZE,
            box,
            lift=C.PLAYER_ART_LIFT,
        ),
        ("idle", "down"): strip("player_idle_down.png"),
        ("idle", "up"): strip("player_idle_up.png"),
        ("idle", "right"): strip("player_idle_side.png"),
        ("idle", "left"): strip("player_idle_side.png", flipped=True),
        ("run", "down"): strip("player_run_down.png"),
        ("run", "up"): strip("player_run_up.png"),
        ("run", "right"): strip("player_run_side.png"),
        ("run", "left"): strip("player_run_side.png", flipped=True),
    }


class Player(arcade.Sprite):
    """Sprite du joueur, avec son inventaire et son état de vie."""

    def __init__(self, center_x: float, center_y: float):
        self.animations = _load_player_textures()
        super().__init__(
            self.animations[("idle", "down")][0],
            scale=C.PLAYER_SPRITE_SCALE,
            center_x=center_x,
            center_y=center_y,
        )
        self.inventory = Inventory(capacity=C.INVENTORY_CAPACITY)
        self.is_alive = True

        # Direction d'entrée, remise à jour par la vue à chaque frame.
        self.move_x = 0.0
        self.move_y = 0.0
        self.direction = "down"
        self.facing = (0.0, -1.0)

        # Mort volontaire : le personnage s'effondre à l'écran avant que la vie
        # suivante ne commence. `dying` gèle ses entrées, et la dernière image
        # de l'animation devient le sprite du cadavre laissé sur place.
        self.dying = False
        self._death_elapsed = 0.0
        self._frame_index = 0.0

    # ------------------------------------------------------------------ #
    # Déplacement
    # ------------------------------------------------------------------ #
    def set_movement(self, move_x: float, move_y: float) -> None:
        """Enregistre la direction demandée par le joueur (normalisée)."""
        length = (move_x**2 + move_y**2) ** 0.5
        if length > 0:
            move_x /= length
            move_y /= length
            self.facing = (move_x, move_y)
            # L'axe dominant décide de la bande d'animation affichée.
            if abs(move_x) >= abs(move_y):
                self.direction = "right" if move_x > 0 else "left"
            else:
                self.direction = "up" if move_y > 0 else "down"
        self.move_x = move_x
        self.move_y = move_y

    def apply_movement(self, delta_time: float) -> None:
        """
        Convertit la direction en déplacement pour le moteur physique d'Arcade.

        On multiplie par `delta_time` pour que la vitesse soit en pixels par
        seconde et non par frame : le jeu se comporte pareil à 30 ou 144 fps.
        """
        self.change_x = self.move_x * C.PLAYER_SPEED * delta_time
        self.change_y = self.move_y * C.PLAYER_SPEED * delta_time

    def stop(self) -> None:
        self.move_x = self.move_y = 0.0
        self.change_x = self.change_y = 0.0

    # ------------------------------------------------------------------ #
    # Mort
    # ------------------------------------------------------------------ #
    def start_dying(self) -> None:
        """Déclenche l'animation d'effondrement."""
        self.stop()
        self.dying = True
        self._death_elapsed = 0.0

    @property
    def death_animation_finished(self) -> bool:
        return self._death_elapsed >= C.DEATH_ANIMATION_DURATION

    def _update_death_animation(self, delta_time: float) -> None:
        """Joue la chute une seule fois, puis reste sur le corps au sol."""
        self._death_elapsed += delta_time
        frames = self.animations[("death", "any")]
        progress = min(1.0, self._death_elapsed / C.DEATH_ANIMATION_DURATION)
        self.texture = frames[min(len(frames) - 1, int(progress * len(frames)))]

    def update_animation(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """Fait tourner l'animation correspondant à l'état courant."""
        if self.dying:
            self._update_death_animation(delta_time)
            return

        moving = self.move_x or self.move_y
        state = "run" if moving else "idle"
        frames = self.animations[(state, self.direction)]
        fps = C.PLAYER_RUN_FPS if moving else C.PLAYER_IDLE_FPS
        self._frame_index = (self._frame_index + delta_time * fps) % len(frames)
        self.texture = frames[int(self._frame_index)]

    # ------------------------------------------------------------------ #
    # Inventaire (délégué, pour garder un point d'entrée unique)
    # ------------------------------------------------------------------ #
    def pick_up(self, item: Item) -> bool:
        return self.inventory.add(item)

    def has_key(self, key_id: str | None) -> Item | None:
        return self.inventory.find_key(key_id)

    def has_vial(self) -> bool:
        return self.inventory.find(C.ITEM_VIAL) is not None

    def has_torch(self) -> bool:
        return self.inventory.find(C.ITEM_TORCH) is not None

    def respawn_at(self, x: float, y: float) -> None:
        """Nouvelle vie : position de départ, inventaire vidé."""
        self.position = (x, y)
        self.stop()
        self.inventory.clear()
        self.is_alive = True
        self.alpha = 255
        self.direction = "down"
        self.dying = False
        self._death_elapsed = 0.0
        self._frame_index = 0.0
