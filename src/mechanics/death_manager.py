"""
Fichier : death_manager.py
Auteur : base technique (game jam)

Description :
Moteur central du jeu : c'est ici, et nulle part ailleurs, qu'on décide des
conséquences d'une mort.

  - Mort VOLONTAIRE (fiole) ou par PIÈGE : le corps reste dans le labyrinthe.
    Il brille, il a une présence physique, et il conserve tout ce que le joueur
    transportait. C'est un investissement pour la vie suivante.
  - Mort par la CRÉATURE : le corps est dévoré. Aucun cadavre, aucun objet
    récupérable, aucun nouveau repère. La vie est intégralement perdue.

Toute la tension du jeu tient dans cet écart : le joueur doit choisir sa mort
avant que la créature ne la choisisse pour lui.
"""
from __future__ import annotations

from dataclasses import dataclass

from src import constants as C


@dataclass
class DeathResult:
    """Ce qui s'est passé au moment de la mort, pour le HUD et les stats."""

    cause: str
    left_corpse: bool
    items_lost: int
    message: str


class DeathManager:
    """Applique les règles de mort et fait réapparaître le joueur."""

    def __init__(self, audio, score):
        self.audio = audio
        self.score = score
        self.last_result: DeathResult | None = None

    def kill(self, player, level, cause: str) -> DeathResult:
        """Tue le joueur et applique les conséquences liées à la cause."""
        carried = player.inventory.clear()
        # La fiole est unique et ne se transmet jamais à un cadavre : elle
        # réapparaît à sa place d'origine (`level.restore_unique_items`).
        carried = [item for item in carried if item.type != C.ITEM_VIAL]
        leaves_corpse = cause in (C.DEATH_VIAL, C.DEATH_TRAP)

        if leaves_corpse:
            level.add_corpse(player.center_x, player.center_y, carried, cause)
            if cause == C.DEATH_VIAL:
                message = "Tu bois la fiole. Ton corps restera ici, et ce qu'il porte avec."
                self.audio.play("death_vial")
            else:
                message = (
                    "Le piege t'a eu. Ses pointes rentrent et ressortent : "
                    "regarde le rythme et passe entre deux."
                )
                self.audio.play("trap_trigger")
            items_lost = 0
        else:
            message = "Elle t'a devore. Rien ne reste : ni corps, ni objets."
            self.audio.play("devoured")
            items_lost = len(carried)

        self.score.stats.record_death(cause)
        player.is_alive = False

        result = DeathResult(
            cause=cause,
            left_corpse=leaves_corpse,
            items_lost=items_lost,
            message=message,
        )
        self.last_result = result
        return result

    def respawn(self, player, level) -> list[str]:
        """
        Nouvelle vie au point de départ de l'étage, les mains vides.

        Renvoie les objets uniques remis en place (fiole, et clé si la créature
        l'avait détruite), pour que la vue puisse en informer le joueur.
        """
        player.respawn_at(*level.spawn_point)
        restored = level.restore_unique_items(player)
        level.update_zone(player.center_x, player.center_y)
        return restored
