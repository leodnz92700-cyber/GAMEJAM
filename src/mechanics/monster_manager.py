"""
Fichier : monster_manager.py
Auteur : base technique (game jam)

Description :
La menace. Ce module remplace le compte à rebours du jeu : aucun chiffre n'est
affiché au joueur, seule l'ambiance l'informe du temps qu'il lui reste.

Déroulé d'une vie :
  1. calme      : le silence, troue de loin en loin par une goutte d'eau ;
  2. far        : grondements lointains ;
  3. near       : grattements contre les murs, les torches commencent a vaciller ;
  4. close      : des pas courent dans les couloirs, vacillement maximal ;
  5. released   : la créature est lâchée dans le labyrinthe et vient droit sur
                  le joueur. Si elle le touche, il est dévoré (aucun cadavre).

Chaque palier a SON grognement (`audio_manager.TENSION_CUES`), et le meme texte
s'affiche en rouge en haut de l'ecran : le joueur lit et entend la meme chose au
meme instant. A partir du palier `near`, sa respiration s'affole en continu, et
la musique de poursuite demarre des que la creature s'approche — avant qu'elle
ne soit visible.

La créature apparaît loin du joueur puis le rejoint par le plus court chemin.
Elle n'est dessinée qu'à très courte distance : le reste du temps, elle est là
sans être visible.
"""
from __future__ import annotations

import random
from collections import deque

import arcade

from src import constants as C
from src.entities.monster import Monster

# Phrases d'ambiance affichées au joueur à chaque palier. Ce ne sont pas des
# informations chiffrées : elles décrivent ce que le personnage entend.
STAGE_WHISPERS = {
    "calm": "",
    "far": "Quelque chose remue, loin dans la tour.",
    "near": "Des griffes raclent la pierre. Plus pres.",
    "close": "Des pas courent dans le noir. Choisis ou tu meurs.",
    "released": "Elle est la.",
}


def find_path(walkable, start_tile, goal_tile) -> list[tuple[int, int]]:
    """
    Plus court chemin en tuiles (parcours en largeur sur la grille).

    Une grille de 80x40 ne fait que 3200 cases : un BFS complet toutes les
    demi-secondes est largement assez rapide, et évite d'embarquer un A*.
    """
    if start_tile == goal_tile:
        return []
    height = len(walkable)
    width = len(walkable[0]) if height else 0

    def valid(col: int, row: int) -> bool:
        return 0 <= col < width and 0 <= row < height and walkable[row][col]

    if not valid(*goal_tile):
        return []

    parents = {start_tile: None}
    queue = deque([start_tile])
    while queue:
        current = queue.popleft()
        if current == goal_tile:
            break
        col, row = current
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = (col + dx, row + dy)
            if neighbour in parents or not valid(*neighbour):
                continue
            parents[neighbour] = current
            queue.append(neighbour)

    if goal_tile not in parents:
        return []

    path = [goal_tile]
    while parents[path[-1]] is not None:
        path.append(parents[path[-1]])
    path.reverse()
    return path[1:]


class MonsterManager:
    """Gère le sursis, les signaux d'ambiance, puis la traque."""

    def __init__(self, audio):
        self.audio = audio
        self.elapsed = 0.0
        self.stage = "calm"
        self.monster: Monster | None = None
        self.whisper = ""
        self.whisper_timer = 0.0
        self._repath_timer = 0.0
        self._rng = random.Random()

    # ------------------------------------------------------------------ #
    # Cycle de vie
    # ------------------------------------------------------------------ #
    def reset(self) -> None:
        """Nouvelle vie du joueur : le sursis repart de zéro."""
        self.elapsed = 0.0
        self.stage = "calm"
        self.monster = None
        self.whisper = ""
        self.whisper_timer = 0.0
        self._repath_timer = 0.0
        # La bete n'est plus la : la musique de poursuite doit s'arreter net,
        # sans attendre le delai de deconnexion.
        self.audio.stop_chase()

    @property
    def tension(self) -> float:
        """Avancement du sursis, de 0 (début de vie) à 1 (créature lâchée)."""
        return min(1.0, self.elapsed / C.MONSTER_RELEASE_TIME)

    @property
    def is_released(self) -> bool:
        return self.monster is not None

    # ------------------------------------------------------------------ #
    # Mise à jour
    # ------------------------------------------------------------------ #
    def update(self, delta_time: float, player, level) -> bool:
        """
        Fait avancer la menace. Renvoie True si le joueur vient d'être attrapé.
        """
        self.elapsed += delta_time
        self._update_stage(level)

        if self.whisper_timer > 0:
            self.whisper_timer -= delta_time
            if self.whisper_timer <= 0:
                self.whisper = ""

        # La respiration du heros est l'un des trois signaux qui remplacent le
        # compte a rebours : un souffle de temps en temps tant que la bete est
        # loin, un halettement continu des qu'elle se rapproche.
        self.audio.update_breathing(delta_time, self.stage, self.tension)
        level.set_torch_panic(max(0.0, (self.tension - 0.5) * 2.0))

        if self.monster is None:
            self.audio.update_chase(delta_time, near=False)
            return False

        self._chase(delta_time, player, level)
        self.monster.update_visibility(player.center_x, player.center_y)
        distance = arcade.math.get_distance(
            self.monster.center_x, self.monster.center_y, player.center_x, player.center_y
        )
        # La musique de poursuite se declenche plus LOIN que le rayon ou la
        # creature devient visible : le joueur doit l'entendre arriver avant de
        # la voir, sinon il meurt sans avoir eu le temps de fuir.
        self.audio.update_chase(delta_time, near=distance <= C.AUDIO_CHASE_RADIUS)
        return distance <= C.MONSTER_KILL_RADIUS

    def _update_stage(self, level) -> None:
        """Franchit les paliers de tension et déclenche les signaux sonores."""
        current = "calm"
        for threshold, name in C.TENSION_STAGES:
            if self.tension >= threshold:
                current = name
        if current == self.stage:
            return

        self.stage = current
        self.audio.play_tension_cue(current)
        self.whisper = STAGE_WHISPERS.get(current, "")
        self.whisper_timer = 4.0
        if current == "released":
            self._release(level)

    def _release(self, level) -> None:
        """Fait apparaître la créature loin du joueur, dans un couloir."""
        spawn = self._far_spawn_tile(level)
        self.monster = Monster(
            spawn[0] * C.TILE_SIZE + C.TILE_SIZE / 2,
            spawn[1] * C.TILE_SIZE + C.TILE_SIZE / 2,
        )

    def _far_spawn_tile(self, level) -> tuple[int, int]:
        """Choisit une case traversable éloignée du joueur (et non visible)."""
        walkable = level.map.walkable
        candidates = [
            (col, row)
            for row in range(len(walkable))
            for col in range(len(walkable[0]))
            if walkable[row][col]
        ]
        player_zone = level.zone
        far = [
            tile
            for tile in candidates
            if level.map.zone_at(tile[0] * C.TILE_SIZE, tile[1] * C.TILE_SIZE) != player_zone
        ]
        return self._rng.choice(far or candidates)

    def _chase(self, delta_time: float, player, level) -> None:
        """Recalcule périodiquement le chemin, puis avance dessus."""
        self._repath_timer -= delta_time
        if self._repath_timer <= 0 or not self.monster.path:
            self._repath_timer = C.MONSTER_REPATH_INTERVAL
            start = (
                int(self.monster.center_x // C.TILE_SIZE),
                int(self.monster.center_y // C.TILE_SIZE),
            )
            goal = (
                int(player.center_x // C.TILE_SIZE),
                int(player.center_y // C.TILE_SIZE),
            )
            # La créature ignore les portes : elles ne sont un obstacle que pour
            # le joueur. On ne cherche donc un chemin que sur les murs.
            tiles = find_path(level.map.walkable, start, goal)
            self.monster.path = [
                (col * C.TILE_SIZE + C.TILE_SIZE / 2, row * C.TILE_SIZE + C.TILE_SIZE / 2)
                for col, row in tiles
            ]
        self.monster.follow_path(delta_time)
