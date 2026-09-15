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
from src.ui.dialog_box import DialogBox
from src.ui.hud import HUD

# Touches de déplacement (clavier AZERTY + flèches).
KEYS_UP = (arcade.key.Z, arcade.key.UP)
KEYS_DOWN = (arcade.key.S, arcade.key.DOWN)
KEYS_LEFT = (arcade.key.Q, arcade.key.LEFT)
KEYS_RIGHT = (arcade.key.D, arcade.key.RIGHT)

DEATH_BLACKOUT = 0.7        # secondes d'écran noir entre deux vies


class GameView(arcade.View):
    """Le jeu lui-même."""

    def __init__(self, mode: str = C.MODE_FREE, level_index: int = 0,
                 level_names: list[str] | None = None):
        super().__init__()
        self.mode = mode
        self.level_manager = LevelManager(level_names, start_index=level_index)

        self.audio = AudioManager()
        self.score = ScoreManager()
        self.death_manager = DeathManager(self.audio, self.score)
        self.interaction = InteractionManager(self.audio, self.score)
        self.monster_manager = MonsterManager(self.audio)
        self.lighting = LightingEngine(self.window)

        self.hud = HUD()
        # Placé en haut de l'écran : au centre, il masquerait le joueur et la
        # petite zone éclairée autour de lui.
        self.dialog = DialogBox(
            C.WINDOW_WIDTH / 2, C.WINDOW_HEIGHT - 120, 760, 120, font_size=15
        )

        # Caméra du monde : cadrée sur la zone courante, jamais sur le joueur.
        self.camera = arcade.Camera2D(
            viewport=arcade.LBWH(0, C.HUD_HEIGHT, C.VIEWPORT_WIDTH, C.VIEWPORT_HEIGHT)
        )
        self.camera_gui = arcade.Camera2D()

        self.level = None
        self.player: Player | None = None
        self.physics_engine = None

        self.keys_down: set[int] = set()
        self.death_timer = 0.0
        self.zone_fade = 0.0
        self.finished = False      # empêche de déclencher deux fins de partie

    # ------------------------------------------------------------------ #
    # Mise en place
    # ------------------------------------------------------------------ #
    def setup(self) -> None:
        """Prépare une partie complète (appelé une fois avant d'afficher la vue)."""
        self.level = self.level_manager.load_current()
        self.player = Player(*self.level.spawn_point)
        self._rebuild_physics()

        self.score.start_run(self.mode, self.level_manager.current_name)
        self.monster_manager.reset()
        self.level.update_zone(*self.player.position)
        self.score.stats.zones_visited.add(self.level.zone)
        self._snap_camera()

        self.audio.start_ambience()
        self.dialog.show(
            "Tu te reveilles dans le noir. Quelque part au-dessus, il y a une sortie.\n"
            "E : interagir     F : planter une torche     R : boire la fiole",
            duration=5.0,
        )

    def _rebuild_physics(self) -> None:
        """
        (Re)construit le moteur physique.

        Les murs ET les portes fermées bloquent le joueur ; les cadavres non, on
        marche dessus (une dépouille ne doit jamais condamner un couloir).
        """
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, walls=[self.level.wall_list, self.level.door_blocker_list]
        )

    def _snap_camera(self) -> None:
        self.camera.position = self.level.zone_center()

    # ------------------------------------------------------------------ #
    # Boucle de jeu
    # ------------------------------------------------------------------ #
    def on_update(self, delta_time: float) -> None:
        if self.finished:
            return

        self.score.tick(delta_time)
        self.hud.update(delta_time)
        self.dialog.update(delta_time)
        self.level.update_animations(delta_time)
        self.player.update_animation(delta_time)
        if self.monster_manager.monster is not None:
            self.monster_manager.monster.update_animation(delta_time)

        if self.zone_fade > 0:
            self.zone_fade = max(0.0, self.zone_fade - delta_time)

        # Écran noir entre deux vies : le joueur ne contrôle rien.
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
        self.level.update_darts(delta_time)

        if self._check_hazards():
            return
        if self.monster_manager.update(delta_time, self.player, self.level):
            self._die(C.DEATH_DEVOURED)
            return
        if self.level.reached_exit(self.player):
            self._clear_floor()
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

    def _check_hazards(self) -> bool:
        """Pièges à pointes et fléchettes. Renvoie True si le joueur est mort."""
        for trap in self.level.trap_list:
            if not isinstance(trap, SpikeTrap) or not trap.is_lethal:
                continue
            if arcade.check_for_collision(self.player, trap):
                # Le piège se révèle : il ne surprendra plus personne. Il se met
                # à battre visiblement, et le cadavre laissé dessus sert de balise.
                self.level.reveal_trap_group(trap)
                self._die(C.DEATH_TRAP)
                return True

        if arcade.check_for_collision_with_list(self.player, self.level.dart_list):
            self._die(C.DEATH_TRAP)
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
        result = self.death_manager.kill(self.player, self.level, cause)
        self.hud.show_message(result.message, duration=3.4)
        self.player.stop()
        self.death_timer = DEATH_BLACKOUT
        self._check_mode_limits()

    def _respawn(self) -> None:
        if self.finished:
            return
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

    def _clear_floor(self) -> None:
        """Sortie atteinte : étage suivant, ou victoire si c'était le sommet."""
        self.score.stats.floors_cleared += 1
        next_level = self.level_manager.load_next()
        if next_level is None:
            self._victory()
            return

        self.level = next_level
        self.player.respawn_at(*self.level.spawn_point)
        self._rebuild_physics()
        self.monster_manager.reset()
        self.level.update_zone(*self.player.position)
        self._snap_camera()
        self.hud.show_message(
            f"Etage {self.level_manager.floor_number}. La tour continue.", duration=3.0
        )

    def _victory(self) -> None:
        from src.views.victory_view import VictoryView

        self.finished = True
        self.audio.stop_ambience()
        self.score.save_run(victory=True)
        self.window.show_view(VictoryView(self.score.stats))

    def _game_over(self, reason: str) -> None:
        from src.views.game_over_view import GameOverView

        self.finished = True
        self.audio.stop_ambience()
        self.score.save_run(victory=False)
        self.window.show_view(GameOverView(self.score.stats, reason))

    # ------------------------------------------------------------------ #
    # Entrées
    # ------------------------------------------------------------------ #
    def on_key_press(self, key: int, modifiers: int) -> None:
        self.keys_down.add(key)

        if key == arcade.key.ESCAPE:
            self._back_to_menu()
            return
        if self.death_timer > 0 or self.finished:
            return

        if key == arcade.key.E:
            self.hud.show_message(self.interaction.interact(self.player, self.level))
        elif key == arcade.key.F:
            self.hud.show_message(self.interaction.plant_torch(self.player, self.level))
        elif key == arcade.key.R:
            if self.interaction.consume_vial(self.player):
                self._die(C.DEATH_VIAL)
            else:
                self.hud.show_message("Tu n'as pas de fiole. Cherche un piege.")

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.keys_down.discard(key)

    def _back_to_menu(self) -> None:
        from src.views.main_menu import MainMenuView

        self.finished = True
        self.audio.stop_ambience()
        self.window.show_view(MainMenuView())

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
            self.hud.draw(
                self.player, self.level, self.score, self.monster_manager.whisper
            )
            self.dialog.draw()

    def _draw_world(self) -> None:
        """
        Dessine le monde, du sol vers le dessus.

        `pixelated=True` partout : les sprites du pack sont du pixel art, un
        filtrage lisse les rendrait flous.
        """
        level = self.level
        level.floor_list.draw(pixelated=True)
        level.exit_list.draw(pixelated=True)
        level.plate_list.draw(pixelated=True)
        level.trap_list.draw(pixelated=True)
        level.wall_list.draw(pixelated=True)
        level.door_list.draw(pixelated=True)
        level.corpse_list.draw(pixelated=True)
        level.torch_list.draw(pixelated=True)
        level.item_list.draw(pixelated=True)
        level.npc_list.draw(pixelated=True)
        level.dart_list.draw(pixelated=True)
        if self.monster_manager.monster is not None:
            arcade.draw_sprite(self.monster_manager.monster, pixelated=True)
        if self.player.is_alive:
            arcade.draw_sprite(self.player, pixelated=True)

    def _collect_lights(self) -> None:
        """
        Déclare les sources de lumière de la frame, en coordonnées écran.

        C'est ici que se joue la lisibilité du niveau : le joueur voit son petit
        halo, ses torches plantées, et la lueur de ses anciens corps.
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
            # Un cadavre qui porte encore des objets brille plus fort et plus
            # chaud : dans le noir, c'est le seul moyen de retrouver ce qu'on a
            # laissé derrière soi.
            carrying = corpse.has_items
            self.lighting.add_light(
                screen_x,
                screen_y,
                C.CORPSE_LIGHT_RADIUS * corpse.light_intensity()
                * (C.CORPSE_LOOT_LIGHT_FACTOR if carrying else 1.0),
                C.COLOR_CORPSE_LOOT_GLOW if carrying else C.COLOR_CORPSE_GLOW,
                glow=0.30 if carrying else 0.22,
            )

        for exit_sprite in level.exit_list:
            screen_x, screen_y = level.world_to_screen(
                exit_sprite.center_x, exit_sprite.center_y
            )
            self.lighting.add_light(
                screen_x, screen_y, C.EXIT_LIGHT_RADIUS, (150, 255, 200), glow=0.20
            )

    def _draw_fades(self) -> None:
        """Voile noir : changement de zone et écran de mort."""
        alpha = 0
        if self.zone_fade > 0:
            # Fondu symétrique : noir au milieu de la transition.
            progress = self.zone_fade / C.ZONE_TRANSITION_DURATION
            alpha = int(200 * (1.0 - abs(progress - 0.5) * 2))
        if self.death_timer > 0:
            alpha = max(alpha, 235)
        if alpha <= 0:
            return
        arcade.draw_lbwh_rectangle_filled(
            0, C.HUD_HEIGHT, C.WINDOW_WIDTH, C.VIEWPORT_HEIGHT, (0, 0, 0, alpha)
        )
