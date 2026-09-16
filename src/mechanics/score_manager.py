"""
Fichier : score_manager.py
Auteur : base technique (game jam)

Description :
Statistiques de partie et tableau des scores local (data/leaderboard.json).

Les statistiques ne sont pas seulement décoratives : le mode "Sursis" limite le
nombre de morts et le mode "Contre-la-montre" limite le temps, donc la vue de
jeu interroge ce module pour savoir si la partie est perdue.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from src import constants as C


@dataclass
class RunStats:
    """Tout ce qu'on enregistre sur une partie en cours."""

    mode: str = C.MODE_FREE
    level_name: str = ""
    elapsed: float = 0.0
    deaths_total: int = 0
    deaths_by_vial: int = 0
    deaths_by_trap: int = 0
    deaths_devoured: int = 0
    torches_placed: int = 0
    items_picked: int = 0
    corpses_looted: int = 0
    doors_opened: int = 0
    zones_visited: set = field(default_factory=set)

    def record_death(self, cause: str) -> None:
        self.deaths_total += 1
        if cause == C.DEATH_VIAL:
            self.deaths_by_vial += 1
        elif cause in (C.DEATH_TRAP, C.DEATH_ARROW):
            self.deaths_by_trap += 1
        elif cause == C.DEATH_DEVOURED:
            self.deaths_devoured += 1

    def as_lines(self) -> list[tuple[str, str]]:
        """Statistiques prêtes à afficher sur les écrans de fin."""
        minutes, seconds = divmod(int(self.elapsed), 60)
        return [
            ("Temps", f"{minutes:02d}:{seconds:02d}"),
            ("Morts", str(self.deaths_total)),
            ("  dont sacrifices (fiole)", str(self.deaths_by_vial)),
            ("  dont pieges", str(self.deaths_by_trap)),
            ("  dont devore par la bete", str(self.deaths_devoured)),
            ("Torches plantees", str(self.torches_placed)),
            ("Objets ramasses", str(self.items_picked)),
            ("Objets repris pres d'un ancien corps", str(self.corpses_looted)),
            ("Portes ouvertes", str(self.doors_opened)),
            ("Zones explorees", str(len(self.zones_visited))),
        ]

    def to_json(self) -> dict:
        data = asdict(self)
        data["zones_visited"] = len(self.zones_visited)
        return data


class ScoreManager:
    """Gère les stats de la partie en cours et la persistance du classement."""

    def __init__(self):
        self.stats = RunStats()

    def start_run(self, mode: str, level_name: str) -> None:
        self.stats = RunStats(mode=mode, level_name=level_name)

    def tick(self, delta_time: float) -> None:
        self.stats.elapsed += delta_time

    # ------------------------------------------------------------------ #
    # Conditions de défaite liées au mode de jeu
    # ------------------------------------------------------------------ #
    def is_out_of_deaths(self) -> bool:
        limit = C.GAME_MODES[self.stats.mode]["max_deaths"]
        return limit is not None and self.stats.deaths_total >= limit

    def is_out_of_time(self) -> bool:
        limit = C.GAME_MODES[self.stats.mode]["time_limit"]
        return limit is not None and self.stats.elapsed >= limit

    def deaths_remaining(self) -> int | None:
        limit = C.GAME_MODES[self.stats.mode]["max_deaths"]
        return None if limit is None else max(0, limit - self.stats.deaths_total)

    def time_remaining(self) -> float | None:
        limit = C.GAME_MODES[self.stats.mode]["time_limit"]
        return None if limit is None else max(0.0, limit - self.stats.elapsed)

    # ------------------------------------------------------------------ #
    # Tableau des scores local
    # ------------------------------------------------------------------ #
    def load_leaderboard(self) -> list[dict]:
        if not C.LEADERBOARD_PATH.exists():
            return []
        try:
            content = json.loads(C.LEADERBOARD_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return content.get("runs", []) if isinstance(content, dict) else []

    def save_run(self, victory: bool) -> None:
        """Ajoute la partie au classement local, meilleurs temps en premier."""
        runs = self.load_leaderboard()
        entry = self.stats.to_json()
        entry["victory"] = victory
        runs.append(entry)
        runs.sort(key=lambda run: (not run.get("victory"), run.get("elapsed", 1e9)))
        C.DATA_DIR.mkdir(parents=True, exist_ok=True)
        C.LEADERBOARD_PATH.write_text(
            json.dumps({"runs": runs[:20]}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
