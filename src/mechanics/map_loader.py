"""
Fichier : map_loader.py
Auteur : base technique (game jam)

Description :
Charge un niveau Tiled (.tmx) et le traduit en données exploitables par le jeu :
listes de sprites (sol, murs), définitions d'objets (départ, sortie, items,
pièges, plaques, portes, PNJ), grille de navigation pour la créature, et
découpage du niveau en zones de la taille d'un écran.

Ce module ne crée AUCUNE entité de gameplay : il ne fait que lire la carte et
renvoyer des descriptions neutres (`MapObject`). C'est `level_manager` qui
transforme ensuite ces descriptions en entités. Cette séparation permet de
changer de format de carte sans toucher au reste du jeu.

Convention Tiled attendue :
  - calque de tuiles "Floor" : le sol (décoratif)
  - calque de tuiles "Walls" : les murs (collisions)
  - calques d'objets : "Spawn", "Exit", "Doors", "PressurePlates", "Traps",
    "Items", "NPCs" — la CLASSE de l'objet Tiled donne son type
    (spawn, exit, key, vial, torch, spike, archer, pressure_plate,
     door_key, door_plate, npc).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import arcade

from src import constants as C


@dataclass
class MapObject:
    """Description neutre d'un objet posé dans Tiled."""

    layer: str
    type: str
    center_x: float
    center_y: float
    width: float
    height: float
    properties: dict[str, Any] = field(default_factory=dict)
    rotation: float = 0.0
    name: str = ""

    @property
    def position(self) -> tuple[float, float]:
        return self.center_x, self.center_y


@dataclass
class LoadedMap:
    """Résultat du chargement d'un fichier .tmx."""

    name: str
    tile_map: arcade.TileMap
    floor_list: arcade.SpriteList
    wall_list: arcade.SpriteList
    objects: list[MapObject]
    width_tiles: int
    height_tiles: int
    walkable: list[list[bool]]           # [row][col], row 0 = bas du monde
    zone_cols: int
    zone_rows: int

    # ---------------------------------------------------------------- #
    # Accès pratiques
    # ---------------------------------------------------------------- #
    @property
    def width_pixels(self) -> int:
        return self.width_tiles * C.TILE_SIZE

    @property
    def height_pixels(self) -> int:
        return self.height_tiles * C.TILE_SIZE

    @property
    def zone_count_x(self) -> int:
        return max(1, self.width_tiles // self.zone_cols)

    @property
    def zone_count_y(self) -> int:
        return max(1, self.height_tiles // self.zone_rows)

    def objects_of_type(self, *types: str) -> list[MapObject]:
        return [obj for obj in self.objects if obj.type in types]

    def first_of_type(self, type_: str) -> MapObject | None:
        for obj in self.objects:
            if obj.type == type_:
                return obj
        return None

    def zone_at(self, x: float, y: float) -> tuple[int, int]:
        """Zone (colonne, ligne) contenant le point monde donné."""
        zone_x = int(x // (self.zone_cols * C.TILE_SIZE))
        zone_y = int(y // (self.zone_rows * C.TILE_SIZE))
        zone_x = max(0, min(self.zone_count_x - 1, zone_x))
        zone_y = max(0, min(self.zone_count_y - 1, zone_y))
        return zone_x, zone_y

    def zone_origin(self, zone: tuple[int, int]) -> tuple[float, float]:
        """Coin bas-gauche de la zone, en pixels monde."""
        return (
            zone[0] * self.zone_cols * C.TILE_SIZE,
            zone[1] * self.zone_rows * C.TILE_SIZE,
        )

    def zone_center(self, zone: tuple[int, int]) -> tuple[float, float]:
        origin_x, origin_y = self.zone_origin(zone)
        return (
            origin_x + self.zone_cols * C.TILE_SIZE / 2,
            origin_y + self.zone_rows * C.TILE_SIZE / 2,
        )

    def is_walkable_tile(self, col: int, row: int) -> bool:
        if 0 <= row < self.height_tiles and 0 <= col < self.width_tiles:
            return self.walkable[row][col]
        return False

    def is_walkable_point(self, x: float, y: float) -> bool:
        return self.is_walkable_tile(int(x // C.TILE_SIZE), int(y // C.TILE_SIZE))


def _rect_from_shape(shape) -> tuple[float, float, float, float]:
    """
    Convertit la forme d'un objet Tiled en (centre_x, centre_y, largeur, hauteur).

    Arcade renvoie soit un point (x, y), soit une liste de sommets pour les
    rectangles et polygones. Les coordonnées sont déjà dans le repère du jeu
    (origine en bas à gauche), Arcade ayant retourné l'axe Y de Tiled.
    """
    if isinstance(shape, (tuple, list)) and shape and isinstance(shape[0], (int, float)):
        return float(shape[0]), float(shape[1]), float(C.TILE_SIZE), float(C.TILE_SIZE)

    xs = [float(point[0]) for point in shape]
    ys = [float(point[1]) for point in shape]
    width = max(max(xs) - min(xs), 1.0)
    height = max(max(ys) - min(ys), 1.0)
    return (min(xs) + width / 2, min(ys) + height / 2, width, height)


def _build_walkable_grid(
    wall_list: arcade.SpriteList, width_tiles: int, height_tiles: int
) -> list[list[bool]]:
    """Grille de navigation utilisée par la créature (True = traversable)."""
    grid = [[True] * width_tiles for _ in range(height_tiles)]
    for wall in wall_list:
        col = int(wall.center_x // C.TILE_SIZE)
        row = int(wall.center_y // C.TILE_SIZE)
        if 0 <= row < height_tiles and 0 <= col < width_tiles:
            grid[row][col] = False
    return grid


def load_map(map_name: str) -> LoadedMap:
    """
    Charge `assets/maps/<map_name>` et renvoie un `LoadedMap`.

    `map_name` peut être un nom de fichier ("level_01.tmx") ou un chemin complet.
    """
    path = Path(map_name)
    if not path.is_absolute():
        path = C.MAPS_DIR / path
    if not path.exists():
        raise FileNotFoundError(f"Carte introuvable : {path}")

    tile_map = arcade.load_tilemap(
        str(path),
        scaling=1.0,
        layer_options={
            "Walls": {"use_spatial_hash": True},
            "Walls_layer": {"use_spatial_hash": True},
        },
    )

    wall_list = tile_map.sprite_lists.get("Walls") or tile_map.sprite_lists.get("Walls_layer", arcade.SpriteList(use_spatial_hash=True))
    floor_list = tile_map.sprite_lists.get("Floor") or tile_map.sprite_lists.get("Base_layer", arcade.SpriteList())

    objects: list[MapObject] = []
    for layer_name, tiled_objects in tile_map.object_lists.items():
        for tiled_object in tiled_objects:
            center_x, center_y, width, height = _rect_from_shape(tiled_object.shape)
            # Arcade expose la classe Tiled dans `type` ; on retombe sur le nom
            # de l'objet si le level designer a oublié de renseigner la classe.
            object_type = (getattr(tiled_object, "class_", None) or getattr(tiled_object, "type", None) or tiled_object.name or "").strip().lower()
            objects.append(
                MapObject(
                    layer=layer_name,
                    type=object_type,
                    name=tiled_object.name or "",
                    center_x=center_x,
                    center_y=center_y,
                    width=width,
                    height=height,
                    properties=dict(tiled_object.properties or {}),
                    rotation=getattr(tiled_object, "rotation", 0.0) or getattr(tiled_object.shape, "rotation", 0.0) or 0.0,
                )
            )

    properties = tile_map.properties or {}
    zone_cols = int(properties.get("zone_cols", C.ZONE_COLS))
    zone_rows = int(properties.get("zone_rows", C.ZONE_ROWS))

    return LoadedMap(
        name=path.stem,
        tile_map=tile_map,
        floor_list=floor_list,
        wall_list=wall_list,
        objects=objects,
        width_tiles=tile_map.width,
        height_tiles=tile_map.height,
        walkable=_build_walkable_grid(wall_list, tile_map.width, tile_map.height),
        zone_cols=zone_cols,
        zone_rows=zone_rows,
    )
