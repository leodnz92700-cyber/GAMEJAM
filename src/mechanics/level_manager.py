"""
Fichier : level_manager.py
Auteur : base technique (game jam)

Description :
Construit un étage jouable à partir d'une carte Tiled, et gère l'enchaînement
des étages de la tour.

Deux objets ici :
  - `Level` : tout l'état d'un étage (listes de sprites, portes, plaques,
    pièges, cadavres laissés par le joueur) et la simulation de son
    environnement (plaques enfoncées, portes ouvertes, projectiles) ;
  - `LevelManager` : la pile d'étages, pour passer du niveau 1 au niveau 2.

Le découpage en zones vit aussi ici : `Level.zone` indique la zone courante,
et `update_zone()` détecte le franchissement d'une frontière. La caméra ne suit
jamais le joueur, elle se cale sur la zone.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.corpse import Corpse
from src.entities.items import Item, ItemSprite, make_item_from_map_object
from src.entities.npc import NPC
from src.entities.textures import feet_box, load_single
from src.environment.door import Door, make_door_from_map_object
from src.environment.pressure_plate import make_plate_from_map_object
from src.environment.torch import Torch
from src.environment.trap import SkeletonArcher, SpikeTrap, make_trap_from_map_object
from src.mechanics.map_loader import LoadedMap, load_map


class Level:
    """État complet d'un étage en cours de jeu."""

    def __init__(self, loaded_map: LoadedMap, floor_number: int = 1):
        self.map = loaded_map
        self.floor_number = floor_number       # numéro d'étage affiché au joueur

        # --- Listes de sprites, dans l'ordre de dessin --------------------- #
        self.floor_list = loaded_map.floor_list
        self.wall_list = loaded_map.wall_list
        self.exit_list = arcade.SpriteList()
        self.plate_list = arcade.SpriteList()
        self.trap_list = arcade.SpriteList()
        self.door_list = arcade.SpriteList()
        # Sous-ensemble des portes FERMÉES : c'est cette liste que consulte le
        # moteur physique. Ouvrir une porte revient à l'en retirer.
        self.door_blocker_list = arcade.SpriteList(use_spatial_hash=False)
        self.item_list = arcade.SpriteList()
        self.torch_list = arcade.SpriteList()
        self.corpse_list = arcade.SpriteList()
        # Les archers sont dessinés avec les personnages, pas avec le décor :
        # ils mesurent 32x48 et leur tête déborderait sous le mur du haut.
        self.archer_list = arcade.SpriteList()
        self.arrow_list = arcade.SpriteList()
        self.npc_list = arcade.SpriteList()

        self.doors_by_id: dict[str, Door] = {}
        # Emplacement d'origine des objets uniques (fiole, clés) : ils
        # réapparaissent ici s'ils disparaissent du niveau (voir
        # `restore_unique_items`).
        self.unique_item_spawns: list[tuple[str, tuple[float, float], dict]] = []
        # Horloge du niveau : elle cadence les pièges, qui battent tous ensemble.
        self.clock = 0.0
        self.spawn_point: tuple[float, float] = (0.0, 0.0)
        self.exit_rect: tuple[float, float] = (0.0, 0.0)
        self.zone: tuple[int, int] = (0, 0)

        self._build()

    # ------------------------------------------------------------------ #
    # Construction depuis la carte
    # ------------------------------------------------------------------ #
    def _build(self) -> None:
        for map_object in self.map.objects:
            kind = map_object.type

            if kind == "spawn":
                self.spawn_point = map_object.position

            elif kind == "exit":
                # L'escalier fait deux tuiles de haut : on le cale sur la tuile
                # du bas (sa partie haute déborde volontairement sur le mur) et
                # on ne déclenche la sortie que sur cette tuile du bas.
                sprite = arcade.Sprite(
                    load_single("exit.png", tuple(feet_box(32, 64, 32, 32))),
                    center_x=map_object.center_x,
                    center_y=map_object.center_y + C.TILE_SIZE / 2,
                )
                self.exit_list.append(sprite)
                self.exit_rect = map_object.position

            elif kind in ("key", "vial", "torch"):
                self.item_list.append(
                    ItemSprite(make_item_from_map_object(map_object), *map_object.position)
                )
                if kind in C.RESPAWNING_ITEM_TYPES:
                    self.unique_item_spawns.append(
                        (kind, map_object.position, dict(map_object.properties))
                    )

            elif kind in ("door_key", "door_plate"):
                door = make_door_from_map_object(map_object)
                self.door_list.append(door)
                self.door_blocker_list.append(door)
                self.doors_by_id[door.door_id] = door

            elif kind == "pressure_plate":
                self.plate_list.append(make_plate_from_map_object(map_object))

            elif kind in ("spike", "archer", "dart"):
                trap = make_trap_from_map_object(map_object)
                if isinstance(trap, SkeletonArcher):
                    self.archer_list.append(trap)
                else:
                    self.trap_list.append(trap)

            elif kind == "npc":
                lines = str(map_object.properties.get("lines", "...")).split("|")
                self.npc_list.append(
                    NPC(
                        *map_object.position,
                        lines=lines,
                        wants_item=map_object.properties.get("wants_item"),
                    )
                )

    # ------------------------------------------------------------------ #
    # Zones (caméra fixe, changement d'écran aux frontières)
    # ------------------------------------------------------------------ #
    def update_zone(self, x: float, y: float) -> bool:
        """Met à jour la zone courante. Renvoie True si le joueur a changé d'écran."""
        zone = self.map.zone_at(x, y)
        if zone == self.zone:
            return False
        self.zone = zone
        return True

    def zone_center(self) -> tuple[float, float]:
        return self.map.zone_center(self.zone)

    def zone_origin(self) -> tuple[float, float]:
        return self.map.zone_origin(self.zone)

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convertit une position monde en position écran pour la zone courante."""
        origin_x, origin_y = self.zone_origin()
        return x - origin_x, y - origin_y

    # ------------------------------------------------------------------ #
    # Simulation de l'environnement
    # ------------------------------------------------------------------ #
    def open_door(self, door: Door) -> None:
        door.open()
        if door in self.door_blocker_list:
            self.door_blocker_list.remove(door)

    def close_door(self, door: Door) -> None:
        if door.permanent or not door.is_open:
            return
        door.close()
        if door not in self.door_blocker_list:
            self.door_blocker_list.append(door)

    def update_plates(self, player, audio) -> None:
        """
        Synchronise plaques et portes associées.

        Une plaque tenue par un cadavre reste enfoncée indéfiniment : c'est le
        seul moyen de garder une porte ouverte tout en allant ailleurs.
        """
        for plate in self.plate_list:
            if not plate.update_pressed(player, self.corpse_list):
                continue
            audio.play("plate_click", volume=0.5)
            door = self.doors_by_id.get(plate.door_id or "")
            if door is None:
                continue
            if plate.is_pressed:
                self.open_door(door)
            else:
                self.close_door(door)

    def update_archers(self, delta_time: float) -> None:
        """
        Fait tirer les archers et avancer les flèches.

        Les archers tirent SANS CONDITION : ils ne visent pas, ne s'arrêtent
        jamais et ne s'occupent pas de savoir si le joueur est vivant. Une flèche
        est absorbée par un mur, une porte fermée ou un CADAVRE : le joueur
        traverse donc la salle de l'archer en laissant son ancien corps sur la
        trajectoire, qui encaisse les flèches à sa place aussi longtemps qu'il
        reste là.
        """
        for archer in self.archer_list:
            archer.update_emitter(delta_time, self.arrow_list)

        for arrow in list(self.arrow_list):
            arrow.advance(delta_time)
            blocked = (
                arrow.spent
                or arcade.check_for_collision_with_list(arrow, self.wall_list)
                or arcade.check_for_collision_with_list(arrow, self.door_blocker_list)
                or arcade.check_for_collision_with_list(arrow, self.corpse_list)
            )
            if blocked:
                arrow.remove_from_sprite_lists()

    def update_animations(self, delta_time: float) -> None:
        self.clock += delta_time
        for item in self.item_list:
            item.update_animation(delta_time)
        for torch in self.torch_list:
            torch.update(delta_time)
        for corpse in self.corpse_list:
            corpse.update(delta_time)
        for trap in self.trap_list:
            if isinstance(trap, SpikeTrap):
                trap.update_cycle(self.clock)

    def set_torch_panic(self, panic: float) -> None:
        """Transmet le niveau de tension aux torches (elles vacillent plus fort)."""
        for torch in self.torch_list:
            torch.panic = panic

    # ------------------------------------------------------------------ #
    # Cadavres et torches
    # ------------------------------------------------------------------ #
    def _unique_item_exists(self, item_type: str, properties: dict, player=None) -> bool:
        """Cet objet unique existe-t-il encore quelque part dans l'étage ?"""
        key_id = properties.get("key_id")

        def matches(item) -> bool:
            if item.type != item_type:
                return False
            return key_id is None or item.properties.get("key_id") == key_id

        if any(matches(sprite.item) for sprite in self.item_list):
            return True
        if player is not None and any(matches(item) for item in player.inventory):
            return True
        return False

    def restore_unique_items(self, player=None) -> list[str]:
        """
        Remet en place les objets uniques qui ont disparu du niveau.

        Deux cas concrets :
          - la FIOLE, bue ou emportée dans la mort, revient toujours près du
            départ : le sacrifice volontaire reste possible à chaque vie, sans
            jamais pouvoir en faire un stock ;
          - une CLÉ dévorée par la créature revient là où le joueur l'avait
            trouvée. Sans cela, se faire prendre en la portant détruirait le seul
            exemplaire et rendrait l'étage définitivement infinissable.

        Un objet tombé au sol n'est PAS considéré comme perdu : il est toujours
        dans le niveau, et le joueur doit aller le rechercher lui-même.

        Renvoie la liste des types d'objets remis en place.
        """
        restored: list[str] = []
        for item_type, (x, y), properties in self.unique_item_spawns:
            if self._unique_item_exists(item_type, properties, player):
                continue
            self.item_list.append(ItemSprite(Item(item_type, dict(properties)), x, y))
            restored.append(item_type)
        return restored

    def add_corpse(self, x: float, y: float, cause: str) -> Corpse:
        """Laisse le corps du joueur sur place. Il ne contient rien : les objets
        transportés tombent au sol autour de lui (voir `drop_items`)."""
        corpse = Corpse(x, y, cause)
        self.corpse_list.append(corpse)
        return corpse

    def drop_items(self, x: float, y: float, items) -> list[ItemSprite]:
        """
        Éparpille les objets transportés sur le sol autour du point de mort.

        Le joueur n'a rien à fouiller : ses affaires sont posées par terre et se
        ramassent comme n'importe quel objet. Elles sont marquées `dropped`, ce
        qui leur donne une petite lueur dorée — sans quoi on ne les retrouverait
        jamais dans le noir — et alimente les statistiques de fin de partie.
        """
        dropped: list[ItemSprite] = []
        for item in items:
            position = self._free_spot_near(x, y, dropped)
            item.properties["dropped"] = True
            sprite = ItemSprite(item, *position)
            self.item_list.append(sprite)
            dropped.append(sprite)
        return dropped

    def _free_spot_near(self, x: float, y: float, already: list) -> tuple[float, float]:
        """
        Cherche une case libre autour du point de mort.

        On s'écarte en cercles concentriques pour ne jamais poser un objet dans
        un mur ni deux objets au même endroit. En dernier recours, tout tombe sur
        le corps lui-même : mieux vaut un tas qu'un objet perdu dans la pierre.
        """
        offsets: list[tuple[float, float]] = []
        for distance in (0.85, 1.4, 2.0):
            step = C.TILE_SIZE * distance
            offsets.extend(
                [
                    (step, 0.0), (-step, 0.0), (0.0, step), (0.0, -step),
                    (step * 0.7, step * 0.7), (-step * 0.7, step * 0.7),
                    (step * 0.7, -step * 0.7), (-step * 0.7, -step * 0.7),
                ]
            )
        # Le point de mort lui-même n'est tenté qu'en dernier : les affaires
        # doivent tomber AUTOUR du corps, pas dessous, sinon on ne les voit pas.
        offsets.append((0.0, 0.0))
        for offset_x, offset_y in offsets:
            spot = (x + offset_x, y + offset_y)
            if not self.map.is_walkable_point(*spot):
                continue
            if any(
                arcade.math.get_distance(*spot, *sprite.position) < C.TILE_SIZE * 0.6
                for sprite in already
            ):
                continue
            return spot
        return (x, y)

    def add_torch(self, x: float, y: float) -> Torch:
        torch = Torch(x, y)
        self.torch_list.append(torch)
        return torch

    def spike_traps(self) -> list[SpikeTrap]:
        return [trap for trap in self.trap_list if isinstance(trap, SpikeTrap)]

    def reached_exit(self, player) -> bool:
        return bool(arcade.check_for_collision_with_list(player, self.exit_list))


class LevelManager:
    """Pile des étages de la tour."""

    def __init__(self, level_names: list[str] | None = None, start_index: int = 0):
        self.level_names = list(level_names or C.LEVELS)
        self.index = start_index
        self.level: Level | None = None

    @property
    def current_name(self) -> str:
        return self.level_names[self.index]

    @property
    def floor_number(self) -> int:
        """Numéro d'étage affiché au joueur (1 = rez-de-chaussée de la tour)."""
        return self.index + 1

    @property
    def has_next(self) -> bool:
        return self.index + 1 < len(self.level_names)

    def load_current(self) -> Level:
        self.level = Level(load_map(self.current_name), floor_number=self.floor_number)
        return self.level

    def load_next(self) -> Level | None:
        """Passe à l'étage suivant, ou None si le joueur est au sommet."""
        if not self.has_next:
            return None
        self.index += 1
        return self.load_current()
