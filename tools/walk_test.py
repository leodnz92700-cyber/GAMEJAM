"""
Fichier : tools/walk_test.py
Auteur : base technique (game jam)

Description :
Fait traverser un niveau au joueur, du départ jusqu'à la sortie, en utilisant le
VRAI moteur de collisions du jeu.

`check_levels.py` valide la carte sur la grille de tuiles ; ce script valide
qu'elle est réellement praticable : c'est lui qui détecte un couloir d'une seule
tuile trop étroit pour la boîte de collision du joueur, une porte mal posée ou un
passage de zone bouché.

Les pièges à pointes battent pendant le test : le script attend que les pointes
rentrent avant d'en franchir un. Si un piège ne redevient jamais franchissable,
le joueur serait définitivement bloqué et le test échoue.

    python tools/walk_test.py                 # tous les niveaux
    python tools/walk_test.py level_01.tmx    # un seul

Toutes les portes sont ouvertes d'office : on teste la navigation, pas les
énigmes (dont `check_levels.py` s'occupe déjà).
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import arcade

from src import constants as C
from src.views.game_view import GameView

MAX_SECONDS = 90.0          # temps simulé maximum pour traverser un étage
STUCK_SECONDS = 4.0         # au-delà, on considère le joueur coincé
STEP = 1 / 60


def tile_path(level, start, goal) -> list[tuple[int, int]]:
    """Plus court chemin en tuiles entre deux points du monde."""
    walkable = level.map.walkable
    start_tile = (int(start[0] // C.TILE_SIZE), int(start[1] // C.TILE_SIZE))
    goal_tile = (int(goal[0] // C.TILE_SIZE), int(goal[1] // C.TILE_SIZE))

    parents = {start_tile: None}
    queue = deque([start_tile])
    while queue:
        current = queue.popleft()
        if current == goal_tile:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = (current[0] + dx, current[1] + dy)
            if neighbour in parents or not level.map.is_walkable_tile(*neighbour):
                continue
            parents[neighbour] = current
            queue.append(neighbour)

    if goal_tile not in parents:
        return []
    path = [goal_tile]
    while parents[path[-1]] is not None:
        path.append(parents[path[-1]])
    path.reverse()
    return path


def check_traps_are_passable(level) -> list[str]:
    """
    Vérifie que chaque piège à pointes redevient franchissable.

    Un piège barre toute la largeur d'un couloir d'une tuile : s'il restait
    mortel en permanence, le niveau deviendrait infranchissable. On simule un
    cycle complet et on exige une fenêtre sûre assez longue pour traverser une
    tuile sans se presser.
    """
    problems: list[str] = []
    crossing_time = C.TILE_SIZE / C.PLAYER_SPEED       # ~0.17 s pour franchir une tuile
    required = crossing_time * 3.5
    for trap in level.spike_traps():
        safe = 0.0
        longest = 0.0
        steps = int(C.SPIKE_CYCLE_DURATION / STEP) + 2
        for step in range(steps):
            trap.update_cycle(step * STEP)
            if trap.is_lethal:
                safe = 0.0
            else:
                safe += STEP
                longest = max(longest, safe)
        if longest < required:
            col = int(trap.center_x // C.TILE_SIZE)
            row = int(trap.center_y // C.TILE_SIZE)
            problems.append(
                f"piege en ({col}, {row}) : fenetre sure de {longest:.2f} s seulement, "
                f"il en faut {required:.2f} s pour le traverser"
            )
    return problems


def traps_on_route(level, waypoints) -> int:
    """Nombre de pièges réellement rencontrés sur le trajet emprunté."""
    count = 0
    for trap in level.spike_traps():
        if any(
            abs(x - trap.center_x) < C.TILE_SIZE and abs(y - trap.center_y) < C.TILE_SIZE
            for x, y in waypoints
        ):
            count += 1
    return count


def _step_would_be_lethal(view: GameView, level) -> bool:
    """Le pas qui vient d'etre calcule ferait-il entrer le joueur dans des pointes ?"""
    lethal = [trap for trap in level.spike_traps() if trap.is_lethal]
    if not lethal:
        return False
    original = view.player.position
    view.player.position = (
        original[0] + view.player.change_x,
        original[1] + view.player.change_y,
    )
    touched = any(arcade.check_for_collision(view.player, trap) for trap in lethal)
    view.player.position = original
    return touched


def walk(view: GameView) -> tuple[bool, str]:
    """Pilote le joueur le long du chemin. Renvoie (succès, message)."""
    level = view.level
    for door in list(level.door_list):
        level.open_door(door)

    # On vise `exit_rect` et non le sprite : l'escalier est dessine deux tuiles
    # plus haut que la tuile qui declenche reellement la sortie.
    waypoints = [
        (col * C.TILE_SIZE + C.TILE_SIZE / 2, row * C.TILE_SIZE + C.TILE_SIZE / 2)
        for col, row in tile_path(level, view.player.position, level.exit_rect)
    ]
    if not waypoints:
        return False, "aucun chemin en tuiles entre le depart et la sortie"

    crossed = traps_on_route(level, waypoints)
    elapsed = 0.0
    stuck = 0.0
    waited = 0.0
    index = 0
    last_position = view.player.position

    while elapsed < MAX_SECONDS:
        level.clock += STEP
        for trap in level.spike_traps():
            trap.update_cycle(level.clock)

        target = waypoints[index]
        dx = target[0] - view.player.center_x
        dy = target[1] - view.player.center_y
        if (dx * dx + dy * dy) ** 0.5 < 6.0:
            index += 1
            if index >= len(waypoints):
                return True, (
                    f"sortie atteinte en {elapsed:.1f} s simulees, "
                    f"{crossed} piege(s) franchi(s), "
                    f"{waited:.1f} s d'attente devant les pointes"
                )
            continue

        view.player.set_movement(dx, dy)
        view.player.apply_movement(STEP)

        if _step_would_be_lethal(view, level):
            # Les pointes sont sorties : on patiente au lieu de s'empaler.
            view.player.stop()
            waited += STEP
            elapsed += STEP
            if waited > C.SPIKE_CYCLE_DURATION * 3:
                return False, (
                    "piege infranchissable : ses pointes ne rentrent jamais "
                    "assez longtemps pour laisser passer"
                )
            continue

        view.physics_engine.update()
        level.update_zone(*view.player.position)

        moved = arcade.math.get_distance(*view.player.position, *last_position)
        stuck = 0.0 if moved > 0.4 else stuck + STEP
        if stuck > STUCK_SECONDS:
            col = int(view.player.center_x // C.TILE_SIZE)
            row = int(view.player.center_y // C.TILE_SIZE)
            return False, (
                f"joueur coince en tuile ({col}, {row}) en visant "
                f"({int(target[0] // C.TILE_SIZE)}, {int(target[1] // C.TILE_SIZE)}) "
                f"- couloir trop etroit ou passage bouche ?"
            )
        last_position = view.player.position
        elapsed += STEP

    return False, f"sortie non atteinte en {MAX_SECONDS:.0f} s simulees"


def main() -> None:
    names = sys.argv[1:] or [C.TEST_LEVEL, C.LEVEL_NAME]
    window = arcade.Window(C.WINDOW_WIDTH, C.WINDOW_HEIGHT, "walk test", visible=False)
    failed = False
    for name in names:
        view = GameView(level_name=name)
        view.setup()
        window.show_view(view)

        trap_problems = check_traps_are_passable(view.level)
        for problem in trap_problems:
            print(f"{name} : ECHEC - {problem}")

        success, message = walk(view)
        print(f"{name} : {'OK' if success else 'ECHEC'} - {message}")
        failed = failed or not success or bool(trap_problems)
    window.close()
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
