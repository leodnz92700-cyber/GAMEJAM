"""
Fichier : death_manager.py
Auteur : base technique (game jam)

Description :
Moteur central du jeu : c'est ici, et nulle part ailleurs, qu'on décide des
conséquences d'une mort.

  - Mort VOLONTAIRE (fiole), par PIÈGE ou par FLÈCHE : le corps reste dans le
    labyrinthe.
    Il brille, il a une présence physique, et tout ce que le joueur transportait
    tombe au sol autour de lui, prêt à être ramassé. C'est un investissement pour
    la vie suivante.
    En plus de cela, une COPIE de chaque objet transporté réapparaît à son
    emplacement d'origine dans la carte. Les objets se dupliquent donc à chaque
    mort qui laisse un cadavre : c'est voulu. Le labyrinthe se remplit d'objets à des endroits
    de plus en plus variés, mourir devient un vrai gain, et le joueur n'est
    jamais forcé de retraverser tout l'étage pour récupérer une clé tombée près
    d'un ancien corps.
  - Mort par la CRÉATURE : le corps est dévoré. Aucun cadavre, aucune affaire au
    sol, aucun nouveau repère — la vie est perdue pour rien. Les objets
    transportés, eux, retournent quand même à leur emplacement d'origine : la
    créature prive le joueur du repère qu'il aurait laissé, pas de la clé qu'il
    portait.

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
        # TOUT ce que le joueur portait tombe : plus aucune exception par type
        # d'objet. Ce qui distingue les morts entre elles, c'est la cause, pas
        # le contenu du sac.
        carried = player.inventory.clear()
        leaves_corpse = cause in (C.DEATH_VIAL, C.DEATH_TRAP, C.DEATH_ARROW)

        # QUELLE QUE SOIT la cause, ce que le joueur portait retourne a son
        # emplacement de level design. Ce qui se joue a la mort, ce n'est pas la
        # destruction des objets — le labyrinthe les remet toujours a leur place
        # — c'est le CADAVRE et le tas d'affaires posees a l'endroit precis ou
        # l'on est tombe. La creature prive le joueur de ce repere-la, pas de la
        # cle qu'il portait.
        level.respawn_carried_at_origin(carried)

        if leaves_corpse:
            # Le corps reste sur place, et les affaires tombent autour de lui,
            # en plus des exemplaires revenus a leur place d'origine.
            level.add_corpse(player.center_x, player.center_y, cause)
            level.drop_items(player.center_x, player.center_y, carried)
            if cause == C.DEATH_VIAL:
                # Pas de son ici : la gorgee a deja sonne au moment ou le joueur
                # a bu (`interaction_manager.consume_vial`), et le cri de douleur
                # des morts subies a sonne a l'impact (`game_view._die`). Quand
                # on arrive dans cette methode, le corps est deja au sol.
                message = "Tu bois la fiole. Ton corps reste ici, et tes affaires avec."
            elif cause == C.DEATH_ARROW:
                # C'est LA mort qui enseigne le jeu : le corps qu'on vient de
                # laisser est déjà en travers de la ligne de tir.
                message = (
                    "Une fleche t'a traverse. L'archer ne s'arretera pas : "
                    "ton corps, lui, arrete les fleches."
                )
            else:
                message = (
                    "Mauvais timing. Les pointes rentrent et ressortent : "
                    "attends ton tour et passe entre deux."
                )
            items_lost = 0
        else:
            message = (
                "Elle t'a devore. Pas de corps, pas de repere : "
                "tes affaires sont retournees la ou tu les avais trouvees."
            )
            # La creature tue sur-le-champ : ce son-la part bien au bon moment,
            # en meme temps que l'eclair du jumpscare.
            self.audio.play("monster_kill")
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
