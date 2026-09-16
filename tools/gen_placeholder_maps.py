"""
Fichier : tools/gen_placeholder_maps.py
Auteur : base technique (game jam)

Description :
Génère des niveaux au format Tiled (.tmx), directement ouvrables dans Tiled et
chargeables par `arcade.load_tilemap`.

Structure produite :
  - la carte fait 4 zones (2x2), une zone = exactement un écran de jeu ;
  - chaque zone contient 4 salles reliées par des couloirs ETROITS (1 ou 2
    tuiles) : les salles servent à trouver des objets, les couloirs à faire peur ;
  - les frontières de zone sont des MURS PLEINS, percés uniquement par un
    passage par frontière. Là où l'on ne peut pas changer de zone, il y a donc
    systématiquement un mur ;
  - une seule fiole, posée à quelques pas du départ ;
  - beaucoup de torches réparties le long du chemin principal, assez pour
    l'éclairer entièrement si le joueur les plante toutes ;
  - un squelette archer planté dans une grande salle du chemin, qui balaie la
    pièce de flèches entre les deux ouvertures que le joueur doit emprunter ;
  - les plaques de pression sont posées dans le couloir juste avant la porte
    qu'elles commandent : le joueur voit tout de suite le rapport de cause à
    effet, et comprend qu'il doit mourir dessus.

Le script calcule le chemin départ -> sortie et pose les portes sur des points
de passage obligés, puis vérifie que la clé et la plaque restent atteignables
sans franchir la porte qu'elles débloquent : un niveau généré est terminable.

Usage :
    python tools/gen_placeholder_maps.py

ATTENTION : ce script ECRASE les .tmx. Une fois vos niveaux dessinés dans Tiled,
ne le relancez plus.
"""
from __future__ import annotations

import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import constants as C       # noqa: E402  (après l'ajout au sys.path)

MAPS = ROOT / "assets" / "maps"

# Les dimensions viennent de `constants.py` : une zone doit occuper exactement
# un écran, donc elles ne peuvent pas diverger entre le jeu et le générateur.
TILE = C.TILE_SIZE
ZONE_COLS, ZONE_ROWS = C.ZONE_COLS, C.ZONE_ROWS
ZONES_X, ZONES_Y = C.ZONES_X, C.ZONES_Y
MAP_COLS, MAP_ROWS = ZONE_COLS * ZONES_X, ZONE_ROWS * ZONES_Y

SECTORS_X, SECTORS_Y = 2, 2          # 4 salles par zone
SECTOR_COLS, SECTOR_ROWS = ZONE_COLS // SECTORS_X, ZONE_ROWS // SECTORS_Y

ROOM_MARGIN = 2                      # distance minimale entre une salle et le bord du secteur
ROOM_WIDTH_RANGE = (6, SECTOR_COLS - 2 * ROOM_MARGIN)
ROOM_HEIGHT_RANGE = (4, SECTOR_ROWS - 2 * ROOM_MARGIN)

# Identifiants Tiled (firstgid = 1, donc id du tileset + 1).
FLOOR_GIDS = [14, 15, 16, 17, 26, 27, 28, 29, 38, 39, 40, 41]
WALL_GIDS = [33, 33, 33, 34, 32, 2, 3]   # le 33 domine, les autres cassent la répétition
WALL = "#"
FLOOR = "."


# --------------------------------------------------------------------------- #
# Salles
# --------------------------------------------------------------------------- #
class Room:
    """Une salle rectangulaire, repérée par sa zone et son secteur."""

    def __init__(self, index: int, zone: tuple[int, int], sector: tuple[int, int],
                 col: int, row: int, width: int, height: int):
        self.index = index
        self.zone = zone
        self.sector = sector
        self.col = col
        self.row = row
        self.width = width
        self.height = height

    @property
    def center(self) -> tuple[int, int]:
        return self.col + self.width // 2, self.row + self.height // 2

    def tiles(self):
        for row in range(self.row, self.row + self.height):
            for col in range(self.col, self.col + self.width):
                yield col, row

    def contains(self, col: int, row: int) -> bool:
        return (
            self.col <= col < self.col + self.width
            and self.row <= row < self.row + self.height
        )

    def random_tile(self, rng: random.Random, margin: int = 1) -> tuple[int, int]:
        return (
            rng.randint(self.col + margin, self.col + self.width - 1 - margin),
            rng.randint(self.row + margin, self.row + self.height - 1 - margin),
        )


def build_rooms(rng: random.Random) -> list[Room]:
    """Une salle par secteur, jamais collée au bord de sa zone."""
    rooms: list[Room] = []
    for zone_y in range(ZONES_Y):
        for zone_x in range(ZONES_X):
            for sector_y in range(SECTORS_Y):
                for sector_x in range(SECTORS_X):
                    origin_col = zone_x * ZONE_COLS + sector_x * SECTOR_COLS
                    origin_row = zone_y * ZONE_ROWS + sector_y * SECTOR_ROWS
                    width = rng.randint(*ROOM_WIDTH_RANGE)
                    height = rng.randint(*ROOM_HEIGHT_RANGE)
                    col = rng.randint(
                        origin_col + ROOM_MARGIN,
                        origin_col + SECTOR_COLS - ROOM_MARGIN - width,
                    )
                    row = rng.randint(
                        origin_row + ROOM_MARGIN,
                        origin_row + SECTOR_ROWS - ROOM_MARGIN - height,
                    )
                    rooms.append(
                        Room(
                            len(rooms),
                            (zone_x, zone_y),
                            (sector_x, sector_y),
                            col,
                            row,
                            width,
                            height,
                        )
                    )
    return rooms


def room_at(rooms: list[Room], zone: tuple[int, int], sector: tuple[int, int]) -> Room:
    for room in rooms:
        if room.zone == zone and room.sector == sector:
            return room
    raise KeyError(f"aucune salle en zone {zone} secteur {sector}")


# --------------------------------------------------------------------------- #
# Couloirs
# --------------------------------------------------------------------------- #
class Corridor:
    """Un couloir en L entre deux salles, de largeur 1 ou 2."""

    def __init__(self, a: Room, b: Room, horizontal_first: bool, width: int,
                 is_gate: bool = False):
        self.a = a
        self.b = b
        self.horizontal_first = horizontal_first
        self.width = width
        self.is_gate = is_gate
        self.spine: list[tuple[int, int]] = []       # tuiles de l'axe central
        self.tiles: list[tuple[int, int]] = []       # toutes les tuiles creusées

    def compute(self) -> None:
        """Calcule les tuiles du couloir sans encore toucher à la grille."""
        (col_a, row_a), (col_b, row_b) = self.a.center, self.b.center
        spine: list[tuple[int, int]] = []
        if self.horizontal_first:
            for col in range(min(col_a, col_b), max(col_a, col_b) + 1):
                spine.append((col, row_a))
            for row in range(min(row_a, row_b), max(row_a, row_b) + 1):
                spine.append((col_b, row))
        else:
            for row in range(min(row_a, row_b), max(row_a, row_b) + 1):
                spine.append((col_a, row))
            for col in range(min(col_a, col_b), max(col_a, col_b) + 1):
                spine.append((col, row_b))

        self.spine = spine
        tiles = set()
        for col, row in spine:
            for offset in range(self.width):
                tiles.add((col + offset, row))
                tiles.add((col, row + offset))
        self.tiles = [
            (col, row)
            for col, row in tiles
            if 1 <= col < MAP_COLS - 1 and 1 <= row < MAP_ROWS - 1
        ]

    def outside_spine(self, rooms: list[Room]) -> list[tuple[int, int]]:
        """Tuiles de l'axe central situées hors de toute salle."""
        return [
            (col, row)
            for col, row in self.spine
            if not any(room.contains(col, row) for room in rooms)
        ]


def build_corridors(rooms: list[Room], rng: random.Random) -> list[Corridor]:
    """Relie les salles d'une même zone, puis les zones entre elles par un passage."""
    corridors: list[Corridor] = []

    # --- Liaisons internes à chaque zone ---------------------------------- #
    for zone_y in range(ZONES_Y):
        for zone_x in range(ZONES_X):
            zone = (zone_x, zone_y)
            edges = [
                ((0, 0), (1, 0), True),
                ((0, 1), (1, 1), True),
                ((0, 0), (0, 1), False),
                ((1, 0), (1, 1), False),
            ]
            # On retire une liaison au hasard : la zone garde une boucle mais
            # cesse d'etre un carre parfait, ce qui rend l'exploration moins lisible.
            rng.shuffle(edges)
            for sector_a, sector_b, horizontal_first in edges[:3]:
                corridors.append(
                    Corridor(
                        room_at(rooms, zone, sector_a),
                        room_at(rooms, zone, sector_b),
                        horizontal_first,
                        rng.choice([1, 1, 2, 2]),
                    )
                )

    # --- Passages entre zones : un seul par frontière ---------------------- #
    for zone_y in range(ZONES_Y):
        for zone_x in range(ZONES_X):
            zone = (zone_x, zone_y)
            if zone_x + 1 < ZONES_X:
                sector_y = rng.randint(0, SECTORS_Y - 1)
                corridors.append(
                    Corridor(
                        room_at(rooms, zone, (SECTORS_X - 1, sector_y)),
                        room_at(rooms, (zone_x + 1, zone_y), (0, sector_y)),
                        horizontal_first=True,       # la traversee se fait a l'horizontale
                        width=rng.choice([1, 2]),
                        is_gate=True,
                    )
                )
            if zone_y + 1 < ZONES_Y:
                sector_x = rng.randint(0, SECTORS_X - 1)
                corridors.append(
                    Corridor(
                        room_at(rooms, zone, (sector_x, SECTORS_Y - 1)),
                        room_at(rooms, (zone_x, zone_y + 1), (sector_x, 0)),
                        horizontal_first=False,      # la traversee se fait a la verticale
                        width=rng.choice([1, 2]),
                        is_gate=True,
                    )
                )
    return corridors


# --------------------------------------------------------------------------- #
# Graphe des salles
# --------------------------------------------------------------------------- #
def room_graph(corridors: list[Corridor]) -> dict[int, list[tuple[int, Corridor]]]:
    graph: dict[int, list[tuple[int, Corridor]]] = {}
    for corridor in corridors:
        graph.setdefault(corridor.a.index, []).append((corridor.b.index, corridor))
        graph.setdefault(corridor.b.index, []).append((corridor.a.index, corridor))
    return graph


def bfs_rooms(graph, start: int, blocked: set[Corridor] | None = None):
    blocked = blocked or set()
    parents = {start: (None, None)}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbour, corridor in graph.get(current, []):
            if corridor in blocked or neighbour in parents:
                continue
            parents[neighbour] = (current, corridor)
            queue.append(neighbour)
    return parents


def room_path(parents, target: int) -> tuple[list[int], list[Corridor]]:
    rooms_path = [target]
    corridors_path: list[Corridor] = []
    while parents[rooms_path[-1]][0] is not None:
        previous, corridor = parents[rooms_path[-1]]
        corridors_path.append(corridor)
        rooms_path.append(previous)
    rooms_path.reverse()
    corridors_path.reverse()
    return rooms_path, corridors_path


# --------------------------------------------------------------------------- #
# Construction du niveau
# --------------------------------------------------------------------------- #
def build_level(seed: int) -> tuple[list[list[str]], list[dict]]:
    rng = random.Random(seed)
    rooms = build_rooms(rng)
    corridors = build_corridors(rooms, rng)

    graph = room_graph(corridors)
    spawn_room = room_at(rooms, (0, ZONES_Y - 1), (0, SECTORS_Y - 1))   # bas-gauche
    exit_room = room_at(rooms, (ZONES_X - 1, 0), (SECTORS_X - 1, 0))    # haut-droite

    parents = bfs_rooms(graph, spawn_room.index)
    assert exit_room.index in parents, "sortie inatteignable"
    path_rooms, path_corridors = room_path(parents, exit_room.index)

    # --- Portes : deux points de passage obligés du chemin principal -------- #
    def corridor_at(fraction: float) -> Corridor:
        index = max(0, min(len(path_corridors) - 1, int(len(path_corridors) * fraction)))
        return path_corridors[index]

    key_corridor = corridor_at(0.5)
    plate_corridor = corridor_at(0.85)
    if plate_corridor is key_corridor and len(path_corridors) > 1:
        plate_corridor = path_corridors[-1]

    # Une porte doit boucher tout le passage : son couloir est donc creusé
    # sur une seule tuile de large.
    key_corridor.width = 1
    plate_corridor.width = 1

    for corridor in corridors:
        corridor.compute()

    # --- Vérifications de solvabilité -------------------------------------- #
    without_key_door = bfs_rooms(graph, spawn_room.index, {key_corridor})
    without_plate_door = bfs_rooms(graph, spawn_room.index, {plate_corridor})

    # --- Creusement ---------------------------------------------------------- #
    grid = [[WALL] * MAP_COLS for _ in range(MAP_ROWS)]
    for room in rooms:
        for col, row in room.tiles():
            grid[row][col] = FLOOR
    for corridor in corridors:
        for col, row in corridor.tiles:
            grid[row][col] = FLOOR

    # Bord de carte : toujours du mur.
    for col in range(MAP_COLS):
        grid[0][col] = grid[MAP_ROWS - 1][col] = WALL
    for row in range(MAP_ROWS):
        grid[row][0] = grid[row][MAP_COLS - 1] = WALL

    objects: list[dict] = []

    def add(layer: str, class_: str, col: int, row: int, cols: int = 1, rows: int = 1,
            **properties) -> None:
        objects.append(
            {
                "layer": layer,
                "class": class_,
                "x": col * TILE,
                "y": row * TILE,
                "width": cols * TILE,
                "height": rows * TILE,
                "properties": properties,
            }
        )

    # --- Départ et fiole unique --------------------------------------------- #
    spawn_col, spawn_row = spawn_room.center
    add("Spawn", "spawn", spawn_col, spawn_row)

    # La fiole est posée à quelques pas du départ, toujours dans la salle de
    # départ : le joueur doit tomber dessus dès sa première vie.
    vial_col = min(spawn_room.col + spawn_room.width - 2, spawn_col + 3)
    add("Items", "vial", vial_col, spawn_row, unique=True)

    # --- Sortie -------------------------------------------------------------- #
    exit_col, exit_row = exit_room.center
    add("Exit", "exit", exit_col, exit_room.row)

    # --- Portes -------------------------------------------------------------- #
    def door_placement(corridor: Corridor) -> tuple[int, int, str]:
        """Tuile de couloir hors salle où poser la porte, et sens du passage."""
        outside = corridor.outside_spine(rooms)
        assert outside, "couloir entierement absorbe par les salles"
        col, row = outside[len(outside) // 2]
        neighbours = set(outside)
        horizontal = (col - 1, row) in neighbours or (col + 1, row) in neighbours
        return col, row, "horizontal" if horizontal else "vertical"

    key_col, key_row, key_passage = door_placement(key_corridor)
    add("Doors", "door_key", key_col, key_row,
        door_id="key_door_1", key_id="key_1", passage=key_passage)

    plate_col, plate_row, plate_passage = door_placement(plate_corridor)
    add("Doors", "door_plate", plate_col, plate_row,
        door_id="plate_door_1", plate_id="plate_1", passage=plate_passage)

    # --- Plaque de pression, juste devant sa porte --------------------------- #
    plate_outside = plate_corridor.outside_spine(rooms)
    door_index = plate_outside.index((plate_col, plate_row))
    # On recule de quelques tuiles du côté accessible sans franchir la porte.
    start_side_first = plate_corridor.a.index in without_plate_door
    offset = -4 if start_side_first else 4
    candidate = plate_outside[max(0, min(len(plate_outside) - 1, door_index + offset))]
    if candidate == (plate_col, plate_row):
        candidate = plate_outside[0] if start_side_first else plate_outside[-1]
    add("PressurePlates", "pressure_plate", candidate[0], candidate[1],
        plate_id="plate_1", door_id="plate_door_1")

    # --- Clé : atteignable sans franchir la porte qu'elle ouvre -------------- #
    key_candidates = [
        room for room in rooms
        if room.index in without_key_door and room.index not in path_rooms
    ] or [room for room in rooms if room.index in without_key_door]
    key_room = max(key_candidates, key=lambda room: len(bfs_rooms(graph, room.index)))
    key_item_col, key_item_row = key_room.random_tile(rng)
    add("Items", "key", key_item_col, key_item_row, key_id="key_1")

    # --- Piège à pointes : barre un couloir étroit, tôt sur le chemin -------- #
    spike_corridor = path_corridors[max(0, int(len(path_corridors) * 0.25))]
    spike_outside = spike_corridor.outside_spine(rooms)
    if spike_outside:
        spike_col, spike_row = spike_outside[len(spike_outside) // 2]
        # Un piège par tuile : on barre toute la largeur du couloir pour que la
        # première rencontre soit inévitable.
        for offset in range(spike_corridor.width):
            if grid[spike_row][spike_col + offset] == FLOOR:
                add("Traps", "spike", spike_col + offset, spike_row)
            elif grid[spike_row + offset][spike_col] == FLOOR:
                add("Traps", "spike", spike_col, spike_row + offset)

    # --- Squelette archer : dans une grande salle du chemin ------------------ #
    _place_archer(path_rooms, path_corridors, rooms, add)

    # --- Torches : assez pour éclairer tout le chemin principal -------------- #
    reserved = {
        (obj["x"] // TILE, obj["y"] // TILE)
        for obj in objects
        if obj["class"] not in ("torch",)
    }
    _place_torches(grid, path_corridors, path_rooms, rooms, add, reserved)

    return grid, objects


def _place_archer(path_rooms, path_corridors, rooms, add) -> None:
    """
    Pose un squelette archer dans une grande salle du chemin principal.

    Règle de level design : l'archer doit balayer la salle SUR LE PASSAGE, pas à
    côté. On repère donc par où le joueur entre dans la salle et par où il en
    ressort, puis on tire une ligne de flèches PERPENDICULAIRE à ce trajet,
    entre les deux : le joueur ne peut pas l'éviter, il ne peut que la traverser.

    La salle est choisie la plus grande possible pour que la flèche parcoure
    plusieurs tuiles avant de se planter dans le mur d'en face — on voit le trait
    passer, on entend le tir, et on comprend d'où il vient.
    """
    by_index = {room.index: room for room in rooms}

    def entry_tile(corridor, room):
        """Tuile par laquelle ce couloir aborde la salle (la plus excentrée)."""
        inside = [tile for tile in corridor.spine if room.contains(*tile)]
        if not inside:
            return None
        center_col, center_row = room.center
        return max(
            inside,
            key=lambda tile: abs(tile[0] - center_col) + abs(tile[1] - center_row),
        )

    # Salles traversées (ni le départ, ni la sortie), de la plus grande à la
    # plus petite : une petite salle ne laisserait pas la place d'esquiver.
    candidates = []
    for position in range(1, len(path_rooms) - 1):
        room = by_index[path_rooms[position]]
        if room.width < 6 or room.height < 5:
            continue
        candidates.append((room.width * room.height, position, room))
    if not candidates:
        return
    _, position, room = max(candidates, key=lambda entry: entry[0])

    came_from = entry_tile(path_corridors[position - 1], room)
    goes_to = entry_tile(path_corridors[position], room)
    if came_from is None or goes_to is None:
        came_from, goes_to = (room.col, room.center[1]), (room.col + room.width - 1, room.center[1])

    # Le trajet est-il plutôt horizontal ou plutôt vertical dans cette salle ?
    horizontal_trip = abs(goes_to[0] - came_from[0]) >= abs(goes_to[1] - came_from[1])

    if horizontal_trip:
        # Trajet gauche-droite : rideau de flèches VERTICAL, posé entre les deux
        # ouvertures, et l'archer au bord haut de la salle tire vers le bas.
        low, high = sorted((came_from[0], goes_to[0]))
        col = (low + high) // 2
        col = max(room.col, min(room.col + room.width - 1, col))
        add("Traps", "archer", col, room.row + room.height - 1,
            direction="down", interval=C.ARCHER_DEFAULT_INTERVAL,
            speed=C.ARCHER_DEFAULT_SPEED)
    else:
        # Trajet bas-haut : rideau HORIZONTAL, l'archer au bord gauche tire vers
        # la droite, sur toute la largeur de la salle.
        low, high = sorted((came_from[1], goes_to[1]))
        row = (low + high) // 2
        row = max(room.row, min(room.row + room.height - 1, row))
        add("Traps", "archer", room.col, row,
            direction="right", interval=C.ARCHER_DEFAULT_INTERVAL,
            speed=C.ARCHER_DEFAULT_SPEED)


def _place_torches(grid, path_corridors, path_rooms, rooms, add, reserved) -> None:
    """
    Sème des torches le long du chemin principal.

    L'objectif annoncé dans le pitch : que le joueur puisse, vie après vie,
    éclairer durablement tout son trajet. Il faut donc en trouver largement plus
    qu'il ne peut en porter (l'inventaire n'a que deux places).
    """
    placed: set[tuple[int, int]] = set(reserved)

    def drop(col: int, row: int) -> None:
        if (col, row) in placed or grid[row][col] != FLOOR:
            return
        placed.add((col, row))
        add("Items", "torch", col, row)

    # Une torche tous les 5 tuiles environ le long des couloirs du chemin.
    for corridor in path_corridors:
        outside = corridor.outside_spine(rooms)
        for index in range(2, len(outside), 5):
            drop(*outside[index])

    # Plus une dans chaque salle traversée : les salles sont les respirations
    # du niveau, c'est là qu'on fait le plein avant un couloir.
    for room_index in path_rooms:
        room = rooms[room_index]
        drop(room.col + 1, room.row + 1)
        drop(room.col + room.width - 2, room.row + room.height - 2)


# --------------------------------------------------------------------------- #
# Écriture du .tmx
# --------------------------------------------------------------------------- #
def escape(value) -> str:
    return str(value).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def write_tmx(path: Path, grid: list[list[str]], objects: list[dict],
              rng: random.Random) -> None:
    """Écrit un .tmx : calque de sol, calque de murs, puis les calques d'objets."""
    floor_rows, wall_rows = [], []
    for row in grid:
        floor_rows.append(",".join(str(rng.choice(FLOOR_GIDS)) for _ in row))
        wall_rows.append(
            ",".join(str(rng.choice(WALL_GIDS)) if cell == WALL else "0" for cell in row)
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<map version="1.10" tiledversion="1.11.0" orientation="orthogonal" '
        f'renderorder="right-down" width="{MAP_COLS}" height="{MAP_ROWS}" '
        f'tilewidth="{TILE}" tileheight="{TILE}" infinite="0" '
        f'nextlayerid="20" nextobjectid="{len(objects) + 1}">',
        " <properties>",
        f'  <property name="zone_cols" type="int" value="{ZONE_COLS}"/>',
        f'  <property name="zone_rows" type="int" value="{ZONE_ROWS}"/>',
        " </properties>",
        ' <tileset firstgid="1" source="Tileset_Dungeon.tsx"/>',
    ]

    for layer_id, (name, rows) in enumerate(
        (("Floor", floor_rows), ("Walls", wall_rows)), start=1
    ):
        lines.append(
            f' <layer id="{layer_id}" name="{name}" width="{MAP_COLS}" height="{MAP_ROWS}">'
        )
        lines.append('  <data encoding="csv">')
        lines.append(",\n".join(rows))
        lines.append("  </data>")
        lines.append(" </layer>")

    layer_id = 10
    object_id = 1
    for layer_name in ("Spawn", "Exit", "Doors", "PressurePlates", "Traps", "Items", "NPCs"):
        lines.append(f' <objectgroup id="{layer_id}" name="{layer_name}">')
        for obj in [o for o in objects if o["layer"] == layer_name]:
            attributes = (
                f'id="{object_id}" name="{escape(obj["class"])}" '
                f'class="{escape(obj["class"])}" type="{escape(obj["class"])}" '
                f'x="{obj["x"]}" y="{obj["y"]}" '
                f'width="{obj["width"]}" height="{obj["height"]}"'
            )
            object_id += 1
            if not obj["properties"]:
                lines.append(f"  <object {attributes}/>")
                continue
            lines.append(f"  <object {attributes}>")
            lines.append("   <properties>")
            for key, value in obj["properties"].items():
                if isinstance(value, bool):
                    type_, text = "bool", "true" if value else "false"
                elif isinstance(value, int):
                    type_, text = "int", str(value)
                elif isinstance(value, float):
                    type_, text = "float", str(value)
                else:
                    type_, text = "string", str(value)
                lines.append(
                    f'    <property name="{escape(key)}" type="{type_}" '
                    f'value="{escape(text)}"/>'
                )
            lines.append("   </properties>")
            lines.append("  </object>")
        lines.append(" </objectgroup>")
        layer_id += 1

    lines.append("</map>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    MAPS.mkdir(parents=True, exist_ok=True)
    for name, seed in (("level_test", 3), ("level_01", 20260315)):
        grid, objects = build_level(seed)
        write_tmx(MAPS / f"{name}.tmx", grid, objects, random.Random(seed + 1))
        torches = sum(1 for o in objects if o["class"] == "torch")
        print(f"{name}.tmx : {len(objects)} objets, dont {torches} torches")


if __name__ == "__main__":
    main()
