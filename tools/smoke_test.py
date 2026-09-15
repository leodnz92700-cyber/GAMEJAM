"""
Fichier : tools/smoke_test.py
Auteur : base technique (game jam)

Description :
Test de fumée : lance le jeu pour de vrai, joue un scénario scripté (deplacements,
ramassage, sacrifice a la fiole, liberation de la creature) et enregistre des
captures d'ecran. Sert a verifier qu'une modification n'a rien casse sans avoir
a rejouer le niveau a la main.

    python tools/smoke_test.py [dossier_de_sortie]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import arcade

from src import constants as C
from src.views.main_menu import MainMenuView

OUT_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/labyrinth_smoke")


class Runner:
    """Exécute un scénario image par image, puis ferme la fenêtre."""

    def __init__(self, window: arcade.Window):
        self.window = window
        self.frame = 0
        self.errors: list[str] = []
        self.steps = self._script()

    def _script(self):
        """(frame, description, action) — action recoit la vue courante."""
        return [
            (2, "menu", lambda view: self.shot("01_menu")),
            (3, "aller sur Entrer", lambda view: view.on_key_press(arcade.key.DOWN, 0)),
            (4, "aller sur Entrer", lambda view: view.on_key_press(arcade.key.DOWN, 0)),
            (5, "demarrer la partie", lambda view: view.on_key_press(arcade.key.ENTER, 0)),
            (10, "partie lancee", lambda view: self.shot("02_spawn")),
            (12, "avancer a droite", lambda view: view.on_key_press(arcade.key.D, 0)),
            (80, "stop", lambda view: view.on_key_release(arcade.key.D, 0)),
            (82, "apres deplacement", lambda view: self.shot("03_marche")),
            (84, "donner une fiole et une torche", self.give_items),
            (86, "planter la torche", lambda view: view.on_key_press(arcade.key.F, 0)),
            (88, "reprendre une torche en main", self.give_spare_torch),
            (90, "torche plantee", lambda view: self.shot("04_torche")),
            (92, "boire la fiole", lambda view: view.on_key_press(arcade.key.R, 0)),
            (150, "cadavre laisse", lambda view: self.shot("05_cadavre")),
            (152, "verifier le cadavre", self.check_corpse),
            (153, "verifier la fiole unique", self.check_vial_respawn),
            (154, "teleporter pres du piege", self.teleport_to_spike),
            (170, "mort par piege", lambda view: self.shot("06_piege")),
            (230, "liberer la creature", self.release_monster),
            (236, "creature lachee", lambda view: self.shot("07_creature")),
            (238, "verifier la creature", self.check_monster),
            (240, "prendre la cle", self.take_key),
            (242, "se faire devorer avec la cle", self.feed_to_monster),
            (300, "verifier le retour de la cle", self.check_key_restored),
            (302, "changer de zone", self.teleport_next_zone),
            (320, "zone suivante", lambda view: self.shot("08_zone")),
            (322, "verifier le changement de zone", self.check_zone),
            (324, "fin", lambda view: arcade.close_window()),
        ]

    # ---------------------------------------------------------------- #
    # Actions scriptées
    # ---------------------------------------------------------------- #
    def give_items(self, view) -> None:
        from src.entities.items import Item

        view.player.inventory.clear()
        view.player.pick_up(Item(C.ITEM_TORCH))
        view.player.pick_up(Item(C.ITEM_VIAL))

    def give_spare_torch(self, view) -> None:
        from src.entities.items import Item

        view.player.pick_up(Item(C.ITEM_TORCH))

    def check_corpse(self, view) -> None:
        corpses = view.level.corpse_list
        if len(corpses) != 1:
            self.errors.append(
                f"mort volontaire : {len(corpses)} cadavre(s) au lieu de 1"
            )
        if len(view.level.torch_list) != 1:
            self.errors.append("la torche plantee n'a pas ete enregistree")
        if corpses and [item.type for item in corpses[0].items] != [C.ITEM_TORCH]:
            self.errors.append(
                "le cadavre devrait porter la torche non plantee, et elle seule "
                f"(il porte {[item.type for item in corpses[0].items]})"
            )

    def check_vial_respawn(self, view) -> None:
        """La fiole est unique : elle doit etre revenue a sa place apres la mort."""
        vials = [s for s in view.level.item_list if s.item.type == C.ITEM_VIAL]
        if len(vials) != 1:
            self.errors.append(
                f"{len(vials)} fiole(s) dans le niveau apres la mort, il en faut 1"
            )
            return
        expected = self.map_spawn_of(view, C.ITEM_VIAL)
        # Les objets au sol flottent de +/- 2 px : on compare a la position
        # d'origine declaree dans la carte, avec la tolerance qui va avec.
        if expected is None or arcade.math.get_distance(*vials[0].position, *expected) > 4:
            self.errors.append("la fiole n'est pas revenue a son emplacement d'origine")

    def teleport_to_spike(self, view) -> None:
        from src.environment.trap import SpikeTrap

        spikes = [t for t in view.level.trap_list if isinstance(t, SpikeTrap)]
        if not spikes:
            self.errors.append("aucun piege a pointes dans la carte")
            return
        view.player.position = spikes[0].position

    def release_monster(self, view) -> None:
        view.monster_manager.elapsed = C.MONSTER_RELEASE_TIME + 0.1

    def check_monster(self, view) -> None:
        if view.monster_manager.monster is None:
            self.errors.append("la creature n'a pas ete liberee")
        deaths = view.score.stats
        if deaths.deaths_by_vial != 1 or deaths.deaths_by_trap != 1:
            self.errors.append(
                f"stats de mort inattendues : fiole={deaths.deaths_by_vial} "
                f"piege={deaths.deaths_by_trap}"
            )

    @staticmethod
    def map_spawn_of(view, item_type: str):
        """Position d'origine d'un objet unique, telle que declaree dans la carte."""
        for kind, position, _ in view.level.unique_item_spawns:
            if kind == item_type:
                return position
        return None

    def take_key(self, view) -> None:
        """Le joueur ramasse la cle du niveau, ou qu'elle soit."""
        keys = [s for s in view.level.item_list if s.item.type == C.ITEM_KEY]
        if not keys:
            self.errors.append("aucune cle dans le niveau")
            return
        self.key_position = self.map_spawn_of(view, C.ITEM_KEY)
        view.player.inventory.clear()
        view.player.pick_up(keys[0].item)
        keys[0].remove_from_sprite_lists()
        self.corpses_before_devour = len(view.level.corpse_list)

    def feed_to_monster(self, view) -> None:
        """Amene la creature sur le joueur : mort par devoration."""
        if view.monster_manager.monster is None:
            self.errors.append("pas de creature a lancer sur le joueur")
            return
        view.monster_manager.monster.position = view.player.position

    def check_key_restored(self, view) -> None:
        """
        Une cle devoree doit revenir a sa place.

        Sans cela, se faire prendre en la portant detruit le seul exemplaire et
        l'etage devient definitivement infinissable.
        """
        stats = view.score.stats
        if stats.deaths_devoured != 1:
            self.errors.append(
                f"mort par devoration non enregistree (devore={stats.deaths_devoured})"
            )
        if len(view.level.corpse_list) != self.corpses_before_devour:
            self.errors.append("la creature a laisse un cadavre alors qu'elle devore tout")

        keys = [s for s in view.level.item_list if s.item.type == C.ITEM_KEY]
        if len(keys) != 1:
            self.errors.append(
                f"{len(keys)} cle(s) apres devoration, il en faut exactement 1"
            )
            return
        if arcade.math.get_distance(*keys[0].position, *self.key_position) > 4:
            self.errors.append("la cle n'est pas revenue a son emplacement d'origine")

    def teleport_next_zone(self, view) -> None:
        self.previous_zone = view.level.zone
        center = view.level.map.zone_center((1, 0))
        # On vise une case traversable proche du centre de la zone voisine.
        for radius in range(0, 20):
            for dx, dy in ((0, 0), (radius, 0), (-radius, 0), (0, radius), (0, -radius)):
                x = center[0] + dx * C.TILE_SIZE
                y = center[1] + dy * C.TILE_SIZE
                if view.level.map.is_walkable_point(x, y):
                    view.player.position = (x, y)
                    return
        self.errors.append("aucune case traversable trouvee dans la zone voisine")

    def check_zone(self, view) -> None:
        if view.level.zone == self.previous_zone:
            self.errors.append("le changement de zone n'a pas ete detecte")

    # ---------------------------------------------------------------- #
    # Plomberie
    # ---------------------------------------------------------------- #
    def shot(self, name: str) -> None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        # On retire le canal alpha : la fenetre rend avec une transparence
        # residuelle, ce qui donne des captures delavees a la relecture.
        arcade.get_image().convert("RGB").save(OUT_DIR / f"{name}.png")

    def tick(self) -> None:
        """Appelé après chaque on_draw : exécute les étapes dues à cette frame."""
        self.frame += 1
        view = self.window.current_view
        for frame, description, action in self.steps:
            if frame != self.frame:
                continue
            try:
                action(view)
            except Exception as error:  # pragma: no cover - c'est le but du test
                self.errors.append(f"{description} : {type(error).__name__}: {error}")


def main() -> None:
    window = arcade.Window(C.WINDOW_WIDTH, C.WINDOW_HEIGHT, C.WINDOW_TITLE)
    runner = Runner(window)

    # On s'accroche à la fin du rendu de la fenêtre : la capture doit avoir lieu
    # une fois l'image complète, pas au milieu d'une frame.
    original_dispatch = window.on_draw

    def on_draw():
        result = original_dispatch()
        runner.tick()
        return result

    window.on_draw = on_draw
    window.show_view(MainMenuView())
    arcade.run()

    if runner.errors:
        print("ECHECS :")
        for error in runner.errors:
            print(" -", error)
        raise SystemExit(1)
    print(f"Test de fumee OK — captures dans {OUT_DIR}")


if __name__ == "__main__":
    main()
