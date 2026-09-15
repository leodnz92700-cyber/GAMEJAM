"""
Fichier : tools/check_levels.py
Auteur : base technique (game jam)

Description :
Vérifie qu'un niveau est terminable AVANT d'y jouer. À lancer après chaque
modification de carte dans Tiled :

    python tools/check_levels.py                 # verifie toutes les cartes
    python tools/check_levels.py level_01.tmx    # une seule carte

Contrôles effectués, sur la grille de tuiles réelle (pas sur le graphe qui a
servi à générer la carte) :
  1. les objets obligatoires sont presents (depart, sortie) ;
  2. la sortie est atteignable depuis le depart, portes ouvertes ;
  3. chaque cle est atteignable SANS franchir la porte qu'elle deverrouille ;
  4. chaque plaque de pression est atteignable sans franchir sa porte ;
  5. il y a exactement UNE fiole, et elle est a quelques pas du depart ;
  6. il y a assez de torches pour eclairer le chemin principal ;
  7. estimation de la duree de parcours, pour tenir la contrainte des 5 minutes.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import constants as C
from src.mechanics.map_loader import load_map


def tile_of(x: float, y: float) -> tuple[int, int]:
    return int(x // C.TILE_SIZE), int(y // C.TILE_SIZE)


def tiles_covered(map_object) -> set[tuple[int, int]]:
    """Toutes les tuiles recouvertes par un objet rectangulaire."""
    left = map_object.center_x - map_object.width / 2
    bottom = map_object.center_y - map_object.height / 2
    covered = set()
    col = int(left // C.TILE_SIZE)
    while col * C.TILE_SIZE < left + map_object.width:
        row = int(bottom // C.TILE_SIZE)
        while row * C.TILE_SIZE < bottom + map_object.height:
            covered.add((col, row))
            row += 1
        col += 1
    return covered


def reachable(loaded, start: tuple[int, int], blocked: set[tuple[int, int]]) -> dict:
    """Distances en tuiles depuis `start`, en traitant `blocked` comme des murs."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = (col + dx, row + dy)
            if neighbour in distances or neighbour in blocked:
                continue
            if not loaded.is_walkable_tile(*neighbour):
                continue
            distances[neighbour] = distances[(col, row)] + 1
            queue.append(neighbour)
    return distances


def check(map_name: str) -> list[str]:
    """Renvoie la liste des problemes trouves (vide = carte valide)."""
    loaded = load_map(map_name)
    problems: list[str] = []

    spawn = loaded.first_of_type("spawn")
    exit_object = loaded.first_of_type("exit")
    if spawn is None:
        return [f"{map_name} : aucun objet de classe 'spawn'"]
    if exit_object is None:
        return [f"{map_name} : aucun objet de classe 'exit'"]

    spawn_tile = tile_of(*spawn.position)
    exit_tile = tile_of(*exit_object.position)

    if not loaded.is_walkable_tile(*spawn_tile):
        problems.append("le point de depart est dans un mur")

    # 2. Sortie atteignable, portes ouvertes.
    open_doors = reachable(loaded, spawn_tile, set())
    if exit_tile not in open_doors:
        problems.append("la sortie est inatteignable depuis le depart")
    else:
        steps = open_doors[exit_tile]
        seconds = steps * C.TILE_SIZE / C.PLAYER_SPEED
        detour = seconds * 2.5  # on ne trouve jamais le chemin optimal dans le noir
        print(
            f"  chemin optimal : {steps} tuiles (~{seconds:.0f} s en ligne droite, "
            f"~{detour / 60:.1f} min avec exploration et morts)"
        )
        if detour > 300:
            problems.append(
                f"parcours estime a {detour / 60:.1f} min : trop long pour la cible de 5 min"
            )

    # 3 et 4. Cles et plaques atteignables sans franchir leur propre porte.
    doors = loaded.objects_of_type("door_key", "door_plate")
    for door in doors:
        door_tiles = tiles_covered(door)
        without_door = reachable(loaded, spawn_tile, door_tiles)

        if door.type == "door_key":
            key_id = door.properties.get("key_id")
            keys = [
                item
                for item in loaded.objects_of_type("key")
                if key_id is None or item.properties.get("key_id") == key_id
            ]
            if not keys:
                problems.append(f"porte '{door.properties.get('door_id')}' sans cle associee")
            for key in keys:
                if tile_of(*key.position) not in without_door:
                    problems.append(
                        f"la cle '{key_id}' est enfermee derriere la porte qu'elle ouvre"
                    )
        else:
            plate_id = door.properties.get("plate_id")
            plates = [
                plate
                for plate in loaded.objects_of_type("pressure_plate")
                if plate.properties.get("plate_id") == plate_id
            ]
            if not plates:
                problems.append(f"porte a plaque '{plate_id}' sans plaque associee")
            for plate in plates:
                if tile_of(*plate.position) not in without_door:
                    problems.append(
                        f"la plaque '{plate_id}' est enfermee derriere sa propre porte"
                    )

    # La fiole est unique et doit rester a portee du depart : c'est elle qui
    # permet de choisir sa mort, et elle reapparait ici a chaque vie.
    vials = loaded.objects_of_type("vial")
    if len(vials) != 1:
        problems.append(
            f"{len(vials)} fiole(s) : le niveau doit en contenir exactement une"
        )
    else:
        steps = reachable(loaded, spawn_tile, set()).get(tile_of(*vials[0].position))
        if steps is None:
            problems.append("la fiole est inatteignable depuis le depart")
        elif steps > 12:
            problems.append(
                f"la fiole est a {steps} tuiles du depart : trop loin, "
                "le joueur doit tomber dessus des sa premiere vie"
            )

    # Sans torches, le joueur ne peut pas transformer durablement le labyrinthe.
    torches = loaded.objects_of_type("torch")
    if len(torches) < 10:
        problems.append(f"seulement {len(torches)} torches : trop peu pour eclairer le chemin")

    return problems


def main() -> None:
    names = sys.argv[1:] or [C.TEST_LEVEL] + C.LEVELS
    failed = False
    for name in names:
        print(f"{name} :")
        problems = check(name)
        if problems:
            failed = True
            for problem in problems:
                print(f"  PROBLEME : {problem}")
        else:
            print("  OK")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
