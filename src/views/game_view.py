"""
Fichier : game_view.py
Auteur : base technique (game jam)

Description :
Vue principale : le labyrinthe. Cette classe ne contient presque aucune règle,
elle ORCHESTRE les modules de `src/mechanics` dans le bon ordre. C'est le
fichier à lire en premier pour comprendre le déroulé d'une frame, et c'est
volontairement celui qu'on modifie le moins quand on ajoute du contenu.

Ordre d'une frame :
  1. entrées clavier -> direction du joueur ;
  2. moteur physique (collisions murs + portes fermées) ;
  3. zone courante (la caméra saute d'un écran à l'autre) ;
  4. environnement : plaques, portes, projectiles ;
  5. dangers : pièges, fléchettes, créature ;
  6. sortie de l'étage ;
  7. rendu : monde -> lumière -> HUD.

La caméra ne suit JAMAIS le joueur : elle est calée sur la zone courante, et
change d'un coup quand le joueur franchit une frontière.
"""
from __future__ import annotations

import arcade

from src import constants as C
from src.entities.player import Player
from src.environment.trap import SpikeTrap
from src.mechanics.audio_manager import AudioManager
from src.mechanics.death_manager import DeathManager
from src.mechanics.interaction_manager import InteractionManager
from src.mechanics.level_manager import LevelManager
from src.mechanics.lighting_engine import LightingEngine
from src.mechanics.monster_manager import MonsterManager
from src.mechanics.score_manager import ScoreManager
from src.ui.hud import HUD
from src.ui.screamer import Screamer
from src.camera_utils import apply_letterbox

# Touches de déplacement (clavier AZERTY + flèches).
KEYS_UP = (arcade.key.Z, arcade.key.UP)
KEYS_DOWN = (arcade.key.S, arcade.key.DOWN)
KEYS_LEFT = (arcade.key.Q, arcade.key.LEFT)
KEYS_RIGHT = (arcade.key.D, arcade.key.RIGHT)

# Court écran noir avant la vie suivante. Il est bref car la mise en scène de la
# mort la précède : chute du personnage pour une mort choisie, jumpscare pour une
# mort subie.
DEATH_BLACKOUT = 0.45


class GameView(arcade.View):
    """Le jeu lui-même."""

    def __init__(self, mode: str = C.MODE_FREE, level_name: str | None = None):
        super().__init__()
        self.mode = mode
        self.level_manager = LevelManager(level_name)

        self.audio = AudioManager()
        self.score = ScoreManager()
        self.death_manager = DeathManager(self.audio, self.score)
        self.interaction = InteractionManager(self.audio, self.score)
        self.monster_manager = MonsterManager(self.audio)
        self.lighting = LightingEngine(self.window)

        self.hud = HUD()
        self.screamer = Screamer()

        # Caméra du monde : cadrée sur la zone courante, jamais sur le joueur.
        # Une zone occupe exactement l'écran, il n'y a donc pas de bandeau.
        self.camera = arcade.Camera2D(
            viewport=arcade.LBWH(0, 0, C.VIEWPORT_WIDTH, C.VIEWPORT_HEIGHT)
        )
        self.camera_gui = arcade.Camera2D(
            viewport=arcade.LBWH(0, 0, C.VIEWPORT_WIDTH, C.VIEWPORT_HEIGHT)
        )

        self.level = None
        self.player: Player | None = None
        self.physics_engine = None

        self.keys_down: set[int] = set()
        # Cause de la mort choisie en cours : le personnage est en train de
        # s'effondrer à l'écran, ses conséquences ne s'appliqueront qu'à la fin
        # de l'animation.
        self.dying_cause: str | None = None
        # Recalculée à chaque frame : ce que le joueur peut faire là où il est.
        # L'ATH s'en sert pour n'afficher l'invite « J » qu'à bon escient.
        self.interaction_target = None
        self.death_timer = 0.0
        self.zone_fade = 0.0
        self.fade_in = 0.5
        self.fade_out = 0.0
        self.next_view = None
        self.finished = False      # empêche de déclencher deux fins de partie

    # ------------------------------------------------------------------ #
    # Mise en place
    # ------------------------------------------------------------------ #
    def setup(self) -> None:
        """Prépare une partie complète (appelé une fois avant d'afficher la vue)."""
        self.on_resize(self.window.width, self.window.height)
        self.level = self.level_manager.load_current()
        self.player = Player(*self.level.spawn_point)
        self._rebuild_physics()

        self.score.start_run(self.mode, self.level_manager.current_name)
        self.monster_manager.reset()
        self.level.update_zone(*self.player.position)
        self.score.stats.zones_visited.add(self.level.zone)
        self._snap_camera()

        self.audio.start_ambience()
        # Les touches ne sont plus rappelées ici : l'ATH les affiche en
        # permanence en bas à droite, et l'invite « J » apparaît toute seule
        # quand il y a quelque chose à faire.
        self.hud.show_message(
            "Tu te reveilles dans le noir. Quelque part, il y a une sortie.",
            duration=4.5,
        )

    def _rebuild_physics(self) -> None:
        """
        (Re)construit le moteur physique.

        Les murs, les portes fermées ET les squelettes archers bloquent le
        joueur. L'archer doit être solide : tant qu'on pouvait le traverser, il
        suffisait de marcher dans son dos pour esquiver ses flèches sans jamais
        payer le passage.

        Les cadavres, eux, ne bloquent pas : on marche dessus, une dépouille ne
        doit jamais condamner un couloir.
        """
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            walls=[
                self.level.wall_list,
                self.level.door_blocker_list,
                self.level.archer_list,
            ],
        )

    def _snap_camera(self) -> None:
        self.camera.position = self.level.zone_center()

    # ------------------------------------------------------------------ #
    # Boucle de jeu
    # ------------------------------------------------------------------ #
    def on_update(self, delta_time: float) -> None:
        if self.fade_in > 0:
            self.fade_in = max(0.0, self.fade_in - delta_time)
        if self.fade_out > 0:
            self.fade_out -= delta_time
            if self.fade_out <= 0 and self.next_view:
                self.window.show_view(self.next_view)
                return

        if self.finished and self.fade_out > 0:
            return
        elif self.finished:
            return

        self.hud.update(delta_time)
        
        self.score.tick(delta_time)
        # Le fond sonore du jeu est le SILENCE : pas de nappe continue, juste
        # une goutte d'eau ou un grincement de temps en temps. C'est ce silence
        # qui rend audibles les grognements de la creature.
        self.audio.update_ambience(delta_time)
        self.level.update_animations(delta_time, self.audio, self.player)
        self.player.update_animation(delta_time)
        if self.monster_manager.monster is not None:
            self.monster_manager.monster.update_animation(delta_time)

        if self.zone_fade > 0:
            self.zone_fade = max(0.0, self.zone_fade - delta_time)

        # Mise en scène de la mort : dans ces trois états, le joueur ne contrôle
        # plus rien et le monde ne peut plus le tuer une seconde fois.
        if self.screamer.active:
            self.interaction_target = None
            self.screamer.update(delta_time)
            if not self.screamer.active:
                self._respawn()
            return

        if self.dying_cause is not None:
            self.interaction_target = None
            if self.player.death_animation_finished:
                self._finish_chosen_death()
            return

        if self.death_timer > 0:
            self.death_timer -= delta_time
            if self.death_timer <= 0:
                self._respawn()
            return

        self._apply_input(delta_time)
        self.physics_engine.update()

        if self.level.update_zone(*self.player.position):
            self._snap_camera()
            self.zone_fade = C.ZONE_TRANSITION_DURATION
            self.score.stats.zones_visited.add(self.level.zone)

        self.level.update_plates(self.player, self.audio)
        self.level.update_archers(delta_time, self.audio, self.player)
        self.interaction_target = self.interaction.find_target(self.player, self.level)

        if self._check_hazards():
            return
        if self.monster_manager.update(delta_time, self.player, self.level):
            self._die(C.DEATH_DEVOURED)
            return
        if self.level.reached_exit(self.player):
            self._victory()
            return

        self._check_mode_limits()

    def _apply_input(self, delta_time: float) -> None:
        move_x = move_y = 0.0
        if self.keys_down & set(KEYS_UP):
            move_y += 1.0
        if self.keys_down & set(KEYS_DOWN):
            move_y -= 1.0
        if self.keys_down & set(KEYS_LEFT):
            move_x -= 1.0
        if self.keys_down & set(KEYS_RIGHT):
            move_x += 1.0
        self.player.set_movement(move_x, move_y)
        self.player.apply_movement(delta_time)
        self.audio.update_footsteps(delta_time, moving=bool(move_x or move_y))

    def _check_hazards(self) -> bool:
        """Pièges à pointes et fléchettes. Renvoie True si le joueur est mort."""
        for trap in self.level.trap_list:
            if not isinstance(trap, SpikeTrap) or not trap.is_lethal:
                continue
            if arcade.check_for_collision(self.player, trap):
                # Les pointes sont sorties au mauvais moment : le joueur voyait
                # le piège, c'est son timing qui l'a trahi.
                self._die(C.DEATH_TRAP)
                return True

        if arcade.check_for_collision_with_list(self.player, self.level.arrow_list):
            self._die(C.DEATH_ARROW)
            return True
        return False

    def _check_mode_limits(self) -> None:
        """Défaites propres aux modes de jeu (morts limitées, temps limité)."""
        if self.score.is_out_of_time():
            self._game_over("Le temps est ecoule. La tour te garde.")
        elif self.score.is_out_of_deaths():
            self._game_over("Tu n'as plus de vies a sacrifier.")

    # ------------------------------------------------------------------ #
    # Mort, réapparition, progression
    # ------------------------------------------------------------------ #
    def _die(self, cause: str) -> None:
        """
        Déclenche la mise en scène de la mort.

        Deux traitements opposés, pour que le joueur SENTE la différence entre
        choisir sa mort et la subir :

          - mort choisie (fiole) ou par piège : le héros s'effondre à l'écran, et
            ce n'est qu'une fois tombé que le corps devient le cadavre laissé sur
            place. Les conséquences ne sont appliquées qu'à ce moment-là ;
          - mort par la créature : sa gueule remplit l'écran. Les conséquences
            sont immédiates, il n'y a de toute façon rien à laisser derrière soi.
        """
        if self.dying_cause is not None or self.screamer.active or self.death_timer > 0:
            return          # une mort est déjà en cours
        self.player.stop()
        if cause in (C.DEATH_TRAP, C.DEATH_ARROW):
            # Le cri sonne MAINTENANT, au moment ou les pointes ou la fleche
            # touchent. `death_manager` n'est appele qu'une seconde plus tard,
            # quand le corps a fini de tomber : le cri y arriverait apres coup.
            self.audio.play("pain")

        if cause == C.DEATH_DEVOURED:
            result = self.death_manager.kill(self.player, self.level, cause)
            self.hud.show_message(result.message, duration=3.4)
            self.screamer.start()
            self._check_mode_limits()
            return

        self.player.start_dying()
        self.dying_cause = cause

    def _finish_chosen_death(self) -> None:
        """Le héros a fini de s'effondrer : son corps reste, ses affaires tombent."""
        cause, self.dying_cause = self.dying_cause, None
        result = self.death_manager.kill(self.player, self.level, cause)
        self.hud.show_message(result.message, duration=3.4)
        self.death_timer = DEATH_BLACKOUT
        self._check_mode_limits()

    def _respawn(self) -> None:
        if self.finished:
            return
        self.screamer.stop()
        self.dying_cause = None
        # `respawn` remet aussi en place les objets uniques disparus.
        restored = self.death_manager.respawn(self.player, self.level)
        if C.ITEM_KEY in restored:
            self.hud.show_message(
                "La cle a ete devoree avec toi. Elle est retournee la ou tu "
                "l'avais trouvee.",
                duration=4.5,
            )
        self.monster_manager.reset()
        self._snap_camera()

    def _victory(self) -> None:
        """Sortie atteinte : le jeu ne compte qu'un niveau, la partie est gagnée."""
        from src.views.victory_view import VictoryView

        self.finished = True
        self.audio.stop_all()
        self.score.save_run(victory=True)
        self.next_view = VictoryView(self.score.stats)
        self.fade_out = 0.5

    def _game_over(self, reason: str) -> None:
        from src.views.game_over_view import GameOverView

        self.finished = True
        self.audio.stop_all()
        self.score.save_run(victory=False)
        self.next_view = GameOverView(self.score.stats, reason)
        self.fade_out = 0.5

    # ------------------------------------------------------------------ #
    # Entrées
    # ------------------------------------------------------------------ #
    def on_key_press(self, key: int, modifiers: int) -> None:
        self.keys_down.add(key)

        if key == arcade.key.ESCAPE:
            self._back_to_menu()
            return
        if key == arcade.key.N:
            # Coupe-son : indispensable pour montrer le jeu dans une salle
            # bruyante ou le laisser tourner sur un stand.
            muted = self.audio.toggle_mute()
            self.hud.show_message("Son coupe." if muted else "Son retabli.")
            return
        if (
            self.death_timer > 0
            or self.dying_cause is not None
            or self.screamer.active
            or self.finished
        ):
            return

        if key == arcade.key.J:
            self.hud.show_message(self.interaction.interact(self.player, self.level))
        elif key == arcade.key.L:
            self.hud.show_message(self.interaction.plant_torch(self.player, self.level))
        elif key == arcade.key.M:
            self.hud.show_message(self.interaction.drop_item(self.player, self.level))
        elif key == arcade.key.K:
            if self.interaction.consume_vial(self.player):
                self._die(C.DEATH_VIAL)
            else:
                self.hud.show_message("Tu n'as pas de fiole. Cherche un piege.")
        elif key == arcade.key.O:
            from src.views.objectives_view import ObjectivesView
            self.keys_down.clear()
            self.window.show_view(ObjectivesView(self))

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.keys_down.discard(key)

    def _back_to_menu(self) -> None:
        from src.views.main_menu import MainMenuView

        self.finished = True
        self.audio.stop_all()
        self.next_view = MainMenuView()
        self.fade_out = 0.5

    # ------------------------------------------------------------------ #
    # Rendu
    # ------------------------------------------------------------------ #
    def on_draw(self) -> None:
        self.clear(color=C.COLOR_BACKGROUND)

        with self.camera.activate():
            self._draw_world()

        with self.camera_gui.activate():
            self._collect_lights()
            self.lighting.draw()
            self._draw_fades()
            self.screamer.draw()
            self.hud.draw(
                self.player,
                self.level,
                self.score,
                self.monster_manager.whisper,
                self.interaction_target,
            )

    def _draw_world(self) -> None:
        """
        Dessine le monde, du sol vers le dessus.

        Deux couches :

          1. le décor plat (sol, plaques, pointes, murs, cadavres, objets), qui
             tient entièrement dans sa tuile et ne peut donc rien cacher ;
          2. tout ce qui est HAUT — portes, squelettes archers, PNJ, créature,
             héros — dessiné du plus lointain au plus proche, c'est-à-dire du
             plus haut à l'écran au plus bas. Ces sprites-là dépassent de leur
             tuile : sans ce tri, un personnage debout au NORD d'une porte ou
             d'un archer serait dessiné par-dessus, alors qu'il est derrière.

        `pixelated=True` partout : les sprites du pack sont du pixel art, un
        filtrage lisse les rendrait flous.
        """
        level = self.level
        level.floor_list.draw(pixelated=True)
        # Ombres peintes sous les decors (calque Tiled optionnel
        # "Shadow_layer") : juste au-dessus du sol, jamais de collision.
        level.shadow_list.draw(pixelated=True)
        level.exit_list.draw(pixelated=True)
        level.plate_list.draw(pixelated=True)
        level.trap_list.draw(pixelated=True)
        level.wall_list.draw(pixelated=True)
        # Decors poses par-dessus les murs (calque Tiled optionnel
        # "Props_layer") : purement visuel, meme ordre que dans Tiled.
        level.props_list.draw(pixelated=True)
        level.corpse_list.draw(pixelated=True)
        level.torch_list.draw(pixelated=True)
        level.item_list.draw(pixelated=True)

        tall = [*level.door_list, *level.archer_list, *level.npc_list]
        if self.monster_manager.monster is not None:
            tall.append(self.monster_manager.monster)
        if self.player.is_alive:
            tall.append(self.player)
        for sprite in sorted(tall, key=lambda sprite: -sprite.center_y):
            arcade.draw_sprite(sprite, pixelated=True)

        # Les flèches passent par-dessus tout le monde : dans le noir, c'est le
        # seul indice de danger, il ne doit jamais être caché par un décor.
        level.arrow_list.draw(pixelated=True)

    def _collect_lights(self) -> None:
        """
        Déclare les sources de lumière de la frame, en coordonnées écran.

        C'est ici que se joue la lisibilité du niveau : le joueur voit son petit
        halo, ses torches plantées et la lueur de ses anciens corps — rien
        d'autre. Les objets au sol n'émettent JAMAIS de lumière : on ne les
        trouve qu'en éclairant l'endroit où ils sont tombés.
        """
        level = self.level
        self.lighting.begin_frame()

        if self.player.is_alive:
            screen_x, screen_y = level.world_to_screen(*self.player.position)
            self.lighting.add_light(
                screen_x, screen_y, C.PLAYER_LIGHT_RADIUS, (255, 246, 226), glow=0.16
            )

        for torch in level.torch_list:
            screen_x, screen_y = level.world_to_screen(torch.center_x, torch.center_y)
            self.lighting.add_light(
                screen_x,
                screen_y,
                C.TORCH_LIGHT_RADIUS * torch.light_intensity(),
                C.COLOR_TORCH_GLOW,
                glow=0.24,
            )

        for corpse in level.corpse_list:
            screen_x, screen_y = level.world_to_screen(corpse.center_x, corpse.center_y)
            self.lighting.add_light(
                screen_x,
                screen_y,
                C.CORPSE_LIGHT_RADIUS * corpse.light_intensity(),
                C.COLOR_CORPSE_GLOW,
                glow=0.22,
            )


        for exit_sprite in level.exit_list:
            screen_x, screen_y = level.world_to_screen(
                exit_sprite.center_x, exit_sprite.center_y
            )
            self.lighting.add_light(
                screen_x, screen_y, C.EXIT_LIGHT_RADIUS, C.COLOR_EXIT_GLOW, glow=0.55
            )

    def _draw_fades(self) -> None:
        """Voile noir : changement de zone, écran de mort, et transitions d'écran."""
        alpha = 0
        if self.zone_fade > 0:
            # Fondu symétrique : noir au milieu de la transition.
            progress = self.zone_fade / C.ZONE_TRANSITION_DURATION
            alpha = int(200 * (1.0 - abs(progress - 0.5) * 2))
        if self.death_timer > 0:
            alpha = max(alpha, 235)
        
        # Transitions entre vues
        if self.fade_in > 0:
            alpha = max(alpha, int((self.fade_in / 0.5) * 255))
        elif self.fade_out > 0:
            alpha = max(alpha, int((1.0 - self.fade_out / 0.5) * 255))
            
        if alpha <= 0:
            return
        arcade.draw_lbwh_rectangle_filled(
            0, 0, C.WINDOW_WIDTH, C.WINDOW_HEIGHT, (0, 0, 0, alpha)
        )

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        apply_letterbox(self.camera, width, height)
        apply_letterbox(self.camera_gui, width, height)
