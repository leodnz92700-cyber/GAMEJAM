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
        """
        (frame, description, action) — action recoit la vue courante.

        Les numeros de frame tiennent compte de la mise en scene de la mort :
        environ 57 frames de chute pour une mort choisie, puis 27 d'ecran noir,
        et environ 84 frames de jumpscare pour une mort par devoration.
        """
        return [
            (2, "menu", lambda view: self.shot("01_menu")),
            # Le menu ne compte plus que trois lignes (mode / entrer / quitter) :
            # une seule descente separe le mode du bouton « Entrer dans la tour ».
            (4, "aller sur Entrer", lambda view: view.on_key_press(arcade.key.DOWN, 0)),
            (5, "demarrer la partie", lambda view: view.on_key_press(arcade.key.ENTER, 0)),
            (10, "partie lancee", lambda view: self.shot("02_spawn")),
            (11, "les pieges sont visibles des le depart", self.check_traps_visible),
            (12, "avancer a droite", lambda view: view.on_key_press(arcade.key.D, 0)),
            (80, "stop", lambda view: view.on_key_release(arcade.key.D, 0)),
            (82, "apres deplacement", lambda view: self.shot("03_marche")),
            (84, "donner une fiole et une torche", self.give_items),
            (86, "planter la torche", lambda view: view.on_key_press(arcade.key.L, 0)),
            (88, "reprendre une torche en main", self.give_spare_torch),
            (90, "torche plantee", lambda view: self.shot("04_torche")),
            (92, "boire la fiole", lambda view: view.on_key_press(arcade.key.K, 0)),
            (118, "le heros s'effondre", lambda view: self.shot("05_chute")),
            (120, "verifier l'animation de chute", self.check_dying),
            (190, "cadavre et affaires au sol", lambda view: self.shot("06_cadavre")),
            (192, "verifier le cadavre", self.check_corpse),
            (193, "verifier la fiole unique", self.check_vial_respawn),
            (195, "teleporter sur le piege", self.teleport_to_spike),
            (215, "mort par piege", lambda view: self.shot("07_piege")),
            (290, "se poser dans la ligne de tir de l'archer", self.enter_arrow_line),
            (302, "l'archer tire", lambda view: self.shot("08_archer")),
            (400, "verifier la mort par fleche", self.check_arrow_death),
            (402, "le corps est reste dans la ligne de tir", lambda view: self.shot("09_bouclier")),
            (404, "relever les tirs de l'archer", self.watch_archer),
            (440, "l'archer tire toujours, le corps encaisse", self.check_corpse_shields),
            (465, "liberer la creature", self.release_monster),
            (471, "creature lachee", lambda view: self.shot("10_creature")),
            (473, "verifier la creature", self.check_monster),
            (475, "prendre la cle", self.take_key),
            (477, "se faire devorer avec la cle", self.feed_to_monster),
            (510, "jumpscare", lambda view: self.shot("11_screamer")),
            (512, "verifier le jumpscare", self.check_screamer),
            (575, "verifier le retour de la cle", self.check_key_restored),
            (577, "changer de zone", self.teleport_next_zone),
            (595, "zone suivante", lambda view: self.shot("12_zone")),
            (597, "verifier le changement de zone", self.check_zone),
            (599, "fin", lambda view: arcade.close_window()),
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

    def check_dying(self, view) -> None:
        """Pendant la chute, rien n'est encore applique : ni cadavre, ni respawn."""
        if not view.player.dying:
            self.errors.append("le heros ne joue pas son animation de mort")
        if view.level.corpse_list:
            self.errors.append("le cadavre apparait avant la fin de la chute")

    def check_corpse(self, view) -> None:
        corpses = view.level.corpse_list
        if len(corpses) != 1:
            self.errors.append(
                f"mort volontaire : {len(corpses)} cadavre(s) au lieu de 1"
            )
        if len(view.level.torch_list) != 1:
            self.errors.append("la torche plantee n'a pas ete enregistree")
        if not corpses:
            return

        # La torche non plantee doit etre tombee AU SOL a cote du corps, et non
        # rangee dans le cadavre : on ne fouille plus les cadavres.
        dropped = [
            sprite for sprite in view.level.item_list
            if sprite.item.properties.get("dropped")
        ]
        if [sprite.item.type for sprite in dropped] != [C.ITEM_TORCH]:
            self.errors.append(
                "la torche devrait etre tombee au sol pres du corps "
                f"(objets au sol : {[s.item.type for s in dropped]})"
            )
            return
        distance = arcade.math.get_distance(*dropped[0].position, *corpses[0].position)
        if distance > C.TILE_SIZE * 2.5:
            self.errors.append(
                f"la torche est tombee a {distance:.0f} px du corps, c'est trop loin"
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

    def check_traps_visible(self, view) -> None:
        """
        Les pieges ne se cachent plus : on les voit, on les esquive.

        C'est un choix de game design : si un piege redevenait invisible, le
        joueur ne pourrait plus le lire et mourrait sans comprendre.
        """
        hidden = [trap for trap in view.level.spike_traps() if trap.alpha < 255]
        if hidden:
            self.errors.append(f"{len(hidden)} piege(s) invisible(s) au depart")

    def teleport_to_spike(self, view) -> None:
        spikes = view.level.spike_traps()
        if not spikes:
            self.errors.append("aucun piege a pointes dans la carte")
            return
        view.player.position = spikes[0].position
        # On cale l'horloge du niveau sur le moment ou les pointes sont sorties,
        # sinon le piege serait inoffensif au moment de la teleportation.
        view.level.clock = C.SPIKE_SAFE_DURATION + 0.2

    def archer(self, view):
        archers = view.level.archer_list
        if not archers:
            self.errors.append("aucun squelette archer dans la carte")
            return None
        return archers[0]

    def enter_arrow_line(self, view) -> None:
        """
        Plante le joueur en travers de la ligne de tir, a quelques tuiles devant.

        C'est la situation que le niveau impose reellement : la ligne de fleches
        coupe le passage entre les deux ouvertures de la salle.
        """
        archer = self.archer(view)
        if archer is None:
            return
        dx, dy = archer.direction
        view.player.position = (
            archer.center_x + dx * C.TILE_SIZE * 3,
            archer.center_y + dy * C.TILE_SIZE * 3,
        )

    def check_arrow_death(self, view) -> None:
        """Une fleche tue, et cette mort laisse un corps (contrairement a la bete)."""
        if view.score.stats.deaths_by_trap < 2:
            self.errors.append(
                "l'archer n'a pas tue le joueur plante dans sa ligne de tir "
                f"(morts par piege : {view.score.stats.deaths_by_trap})"
            )

    def watch_archer(self, view) -> None:
        """Releve l'etat de l'archer et du corps, pour comparaison juste apres."""
        archer = self.archer(view)
        self.shots_before = archer.shots_fired if archer else 0
        corpses = view.level.corpse_list
        self.shield_corpse = corpses[-1] if corpses else None
        if self.shield_corpse is None:
            self.errors.append("la mort par fleche n'a laisse aucun cadavre")

    def check_corpse_shields(self, view) -> None:
        """
        Le coeur de la mecanique : l'archer ne s'arrete JAMAIS, mais le corps
        laisse sur la trajectoire encaisse les fleches a la place du joueur.
        """
        archer = self.archer(view)
        if archer is None or self.shield_corpse is None:
            return
        if archer.shots_fired <= self.shots_before:
            self.errors.append("l'archer a cesse de tirer apres avoir tue le joueur")

        dx, dy = archer.direction
        # Distance parcourue par chaque fleche encore en vol, le long de l'axe de
        # tir : aucune ne doit avoir depasse le corps.
        corpse_distance = (
            (self.shield_corpse.center_x - archer.center_x) * dx
            + (self.shield_corpse.center_y - archer.center_y) * dy
        )
        for arrow in view.level.arrow_list:
            distance = (
                (arrow.center_x - archer.center_x) * dx
                + (arrow.center_y - archer.center_y) * dy
            )
            if distance > corpse_distance + C.TILE_SIZE:
                self.errors.append(
                    "une fleche a traverse le cadavre : le corps ne fait plus bouclier"
                )
                return

    def release_monster(self, view) -> None:
        view.monster_manager.elapsed = C.MONSTER_RELEASE_TIME + 0.1

    def check_monster(self, view) -> None:
        if view.monster_manager.monster is None:
            self.errors.append("la creature n'a pas ete liberee")
        deaths = view.score.stats
        # Deux morts "piege" : les pointes, puis la fleche de l'archer.
        if deaths.deaths_by_vial != 1 or deaths.deaths_by_trap != 2:
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

    def check_screamer(self, view) -> None:
        """Le jumpscare doit etre a l'ecran, et la mort deja enregistree."""
        if not view.screamer.active:
            self.errors.append("aucun jumpscare apres une mort par devoration")
        if view.player.is_alive:
            self.errors.append("le joueur est encore vivant pendant le jumpscare")

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
        if view.screamer.active:
            self.errors.append("le jumpscare n'est pas termine avant la vie suivante")

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
