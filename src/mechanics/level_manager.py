"""
Fichier : level_manager.py
Auteur : base technique (game jam)

Description :
Construit le niveau jouable à partir d'une carte Tiled.

Deux objets ici :
  - `Level` : tout l'état du niveau (listes de sprites, portes, plaques,
    pièges, cadavres laissés par le joueur) et la simulation de son
    environnement (plaques enfoncées, portes ouvertes, projectiles) ;
  - `LevelManager` : le chargement de la carte.

Le jeu ne contient **qu'un seul niveau** : atteindre la sortie termine la
partie. Il n'y a donc ni enchaînement d'étages, ni numéro d'étage à afficher.

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
    """État complet du niveau en cours de jeu."""

    def __init__(self, loaded_map: LoadedMap):
        self.map = loaded_map

        # --- Listes de sprites, dans l'ordre de dessin --------------------- #
        self.floor_list = loaded_map.floor_list
        self.wall_list = loaded_map.wall_list
        # Calques de decoration (voir map_loader.LoadedMap) : purement
        # visuels, jamais interroges par la logique de jeu.
        self.shadow_list = loaded_map.shadow_list
        self.props_list = loaded_map.props_list
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
        self.dead_npcs = []

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

            elif kind in ("exit", "end"):
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

            elif kind in ("key", "vial", "torch", "shield", "potion", "object"):
                item = make_item_from_map_object(map_object)
                # Emplacement de level design de CET objet. Il voyage avec lui
                # dans l'inventaire : quand le joueur meurt en le portant, une
                # copie revient ici (voir `respawn_carried_at_origin`).
                item.properties["origin"] = map_object.position
                self.item_list.append(ItemSprite(item, *map_object.position))
                if item.type in C.RESPAWNING_ITEM_TYPES:
                    self.unique_item_spawns.append(
                        (item.type, map_object.position, dict(item.properties))
                    )

            elif kind in ("door_key", "door_plate", "door"):
                door = make_door_from_map_object(map_object, self.map)
                self.door_list.append(door)
                self.door_blocker_list.append(door)
                self.doors_by_id[door.door_id] = door

            elif kind == "pressure_plate":
                self.plate_list.append(make_plate_from_map_object(map_object))

            elif kind in ("spike", "archer", "dart", "skeleton"):
                trap = make_trap_from_map_object(map_object)
                if isinstance(trap, SkeletonArcher):
                    self.archer_list.append(trap)
                else:
                    self.trap_list.append(trap)

            elif kind in ("npc", "pnj"):
                lines = str(map_object.properties.get("lines", "...")).split("|")
                npc = NPC(
                    *map_object.position,
                    lines=lines,
                    wants_item=map_object.properties.get("wants_item"),
                )
                npc.properties = map_object.properties
                self.npc_list.append(npc)

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
            audio.play("plate_press" if plate.is_pressed else "plate_release")
            door = self.doors_by_id.get(plate.door_id or "")
            if door is None:
                continue
            if plate.is_pressed:
                self.open_door(door)
                # Le battant s'entend, meme si le joueur ne le voit pas d'ici :
                # c'est ce qui lui apprend que la plaque commande une porte.
                audio.play("door_open")
            else:
                self.close_door(door)

    def update_archers(self, delta_time: float, audio=None, listener=None) -> None:
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
            arrow = archer.update_emitter(delta_time, self.arrow_list)
            if arrow is None or audio is None:
                continue
            # Le tir ne s'entend qu'a trois tuiles, et d'autant plus fort qu'on
            # est pres : c'est ce qui previent le joueur qu'il entre dans la
            # ligne de tir avant d'avoir vu l'archer.
            volume = self._audible_volume(archer, listener)
            if volume > 0:
                audio.play("arrow_shot", volume=volume)

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

    @staticmethod
    def _audible_volume(sprite, listener) -> float:
        """
        Volume d'un bruit de decor, selon sa distance au joueur.

        Renvoie 1.0 quand le joueur est dessus, `AUDIO_NEAR_MIN_VOLUME` pile a la
        limite de portee, et 0.0 au-dela. Les pieges battent TOUS en phase et les
        archers tirent trois fois par seconde sans jamais s'arreter : entendus
        depuis tout l'etage, ils deviennent un vacarme ou le joueur ne distingue
        plus rien. Attenues, ils redeviennent une INFORMATION — il entend qu'il
        approche d'un piege, de plus en plus fort, avant meme de le voir.

        La montee n'est pas lineaire (`AUDIO_NEAR_CURVE`) : un bruit qui grandit
        proportionnellement a l'approche s'entend deja beaucoup a mi-distance, et
        le joueur ne perçoit plus le rapprochement. Courbee, elle reste discrete
        de loin et grimpe franchement dans les dernieres tuiles.
        """
        if listener is None:
            return 0.0
        distance = arcade.math.get_distance(
            sprite.center_x, sprite.center_y, listener.center_x, listener.center_y
        )
        if distance >= C.AUDIO_NEAR_RANGE:
            return 0.0
        # `closeness` va de 0 a la limite de portee jusqu'a 1 sur le piege lui-meme.
        closeness = 1.0 - distance / C.AUDIO_NEAR_RANGE
        volume = C.AUDIO_NEAR_MIN_VOLUME + (1.0 - C.AUDIO_NEAR_MIN_VOLUME) * (
            closeness ** C.AUDIO_NEAR_CURVE
        )
        # Le plancher ne peut pas s'arreter net a la limite, sinon le son
        # APPARAIT a 12 % en franchissant la derniere tuile : exactement
        # l'impression d'interrupteur qu'on cherche a eviter. On l'eteint donc
        # progressivement sur la derniere tuile de portee.
        return volume * min(1.0, (C.AUDIO_NEAR_RANGE - distance) / C.TILE_SIZE)

    def update_animations(self, delta_time: float, audio=None, listener=None) -> None:
        self.clock += delta_time
        for item in self.item_list:
            item.update_animation(delta_time)
        for torch in self.torch_list:
            torch.update(delta_time)
        for corpse in self.corpse_list:
            corpse.update(delta_time)
        # Tous les pieges de l'etage battent EN PHASE : c'est ce qui permet au
        # joueur d'apprendre le rythme, mais cela veut dire qu'ils jaillissent
        # tous au meme instant. On ne joue donc leur son QU'UNE FOIS par
        # jaillissement, au volume du piege le PLUS PROCHE : sinon deux pieges
        # cote a cote sonnent deux fois plus fort qu'un seul, alors qu'ils
        # barrent le meme couloir.
        nearest = 0.0
        for trap in self.trap_list:
            if not isinstance(trap, SpikeTrap):
                continue
            trap.update_cycle(self.clock)
            if trap.just_struck and audio is not None:
                nearest = max(nearest, self._audible_volume(trap, listener))
        if nearest > 0:
            audio.play("spike_strike", volume=nearest)

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

    def _item_lies_at(self, item_type: str, x: float, y: float) -> bool:
        """Un objet de ce type est-il pose a cet endroit precis du sol ?"""
        return any(
            sprite.item.type == item_type
            and arcade.math.get_distance(x, y, *sprite.position) < C.TILE_SIZE * 0.6
            for sprite in self.item_list
        )

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
            if item_type == C.ITEM_VIAL:
                # La FIOLE se juge a son emplacement, pas a l'echelle de
                # l'etage : depuis que les objets se dupliquent a chaque mort
                # (`respawn_carried_at_origin`), un exemplaire abandonne a
                # l'autre bout de la carte suffisait a la faire passer pour
                # « toujours presente », et le joueur revivait loin de toute
                # fiole. Or se donner la mort doit rester possible a CHAQUE vie.
                if self._item_lies_at(item_type, x, y):
                    continue
            elif self._unique_item_exists(item_type, properties, player):
                continue
            self.item_list.append(ItemSprite(Item(item_type, dict(properties)), x, y))
            restored.append(item_type)

        # Rien a faire de plus pour les cles donnees par un PNJ : le troc est
        # rejouable a l'infini (`InteractionManager._talk`), et l'objet qu'il
        # reclame fait partie des objets uniques remis en place ci-dessus. Une
        # cle devoree par la creature se re-obtient donc toujours.
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

    def place_item_near(self, x: float, y: float, item) -> ItemSprite:
        """
        Pose UN objet volontairement lache par le joueur, juste a cote de lui.

        Il n'est PAS marque `dropped` : ce n'est pas un objet retrouve pres d'un
        cadavre, il ne doit donc ni luire ni compter comme une fouille de corps.
        On evite la case exacte du joueur pour qu'il puisse le voir tomber.
        """
        item.properties.pop("dropped", None)
        sprite = ItemSprite(item, *self._free_spot_near(x, y, list(self.item_list)))
        self.item_list.append(sprite)
        return sprite

    def respawn_carried_at_origin(self, items) -> list[ItemSprite]:
        """
        Fait REVENIR a son emplacement de depart une copie de chaque objet
        transporte au moment d'une mort qui laisse un cadavre.

        C'est volontairement une DUPLICATION : l'exemplaire tombe pres du corps
        reste ramassable, et un autre attend la ou le joueur l'avait trouve la
        premiere fois. Mourir enrichit donc reellement le labyrinthe — c'est la
        traduction mecanique de « mourir pour mieux avancer » — et le joueur
        n'est jamais oblige de refaire tout le chemin jusqu'a son cadavre pour
        recuperer une cle.

        Seuls les objets POSES DANS LA CARTE ont un emplacement d'origine
        (`properties["origin"]`, renseigne au chargement). Un objet donne par un
        PNJ n'en a pas : il ne tombe que pres du cadavre.

        Rien ne revient quand la creature devore le joueur : `death_manager`
        n'appelle pas cette methode dans ce cas.
        """
        respawned: list[ItemSprite] = []
        for item in items:
            origin = item.properties.get("origin")
            if origin is None:
                continue
            x, y = origin
            # Garde-fou : on n'empile pas dix exemplaires au meme endroit si le
            # joueur meurt plusieurs fois de suite en portant le meme objet.
            if self._item_lies_at(item.type, x, y):
                continue
            properties = dict(item.properties)
            # La copie n'est pas « tombee d'un cadavre » : elle est de retour a
            # sa place de level design, sans la lueur doree des affaires.
            properties.pop("dropped", None)
            sprite = ItemSprite(Item(item.type, properties), x, y)
            self.item_list.append(sprite)
            respawned.append(sprite)
        return respawned

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
    """Charge l'unique niveau du jeu."""

    def __init__(self, level_name: str | None = None):
        # `level_name` n'existe que pour les outils et le drapeau `--map` :
        # une partie normale joue toujours `C.LEVEL_NAME`.
        self.level_name = level_name or C.LEVEL_NAME
        self.level: Level | None = None

    @property
    def current_name(self) -> str:
        return self.level_name

    def load_current(self) -> Level:
        self.level = Level(load_map(self.current_name))
        return self.level
