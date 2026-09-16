"""
Fichier : audio_manager.py
Auteur : base technique (game jam)

Description :
Point d'entrée unique pour tout le son. Aucun autre module ne connaît un nom de
fichier audio : ils demandent un nom LOGIQUE (`"door_open"`, `"alert_close"`) et
ce fichier-ci sait où le trouver. Déposer un nouveau son revient donc à changer
une ligne de `SOUND_FILES`, et son volume se règle dans `C.AUDIO_VOLUMES`.

Le son n'est pas décoratif dans ce jeu : **c'est lui qui remplace le compte à
rebours**. Le joueur n'a aucun chiffre à l'écran pour savoir quand la créature
sera lâchée, il n'a que ce que son personnage entend :

  1. quatre grognements d'alerte, un par palier d'approche (`play_tension_cue`) ;
  2. sa propre respiration, qui passe du souffle occasionnel au halètement
     continu dès que la bête se rapproche (`update_breathing`).

Il y a eu une troisième piste, une musique de poursuite déclenchée à l'approche
de la créature : elle a été RETIRÉE à l'écoute. Dans le noir, sous le halètement
et les grognements, on ne l'entendait pratiquement pas — elle ajoutait de la
matière sonore sans ajouter d'information. Ne la remettez pas sans qu'on le
demande.

Il n'y a **pas de nappe de fond** : le fond sonore du jeu est le silence, troué
au hasard par une goutte d'eau ou un grincement (`update_ambience`). C'est ce
silence qui rend les trois signaux ci-dessus audibles ; une nappe continue les
noierait.

Trois sons n'ont pas encore été livrés (`arrow_shot`, `victory`, `game_over`) :
`tools/gen_placeholder_assets.py` en fabrique des placeholders de synthèse sous
leur nom DÉFINITIF. Déposer le vrai fichier par-dessus suffit, il n'y a pas une
ligne de code à toucher.
"""
from __future__ import annotations

import random

import arcade

from src import constants as C

# Nom logique -> fichier, relatif à assets/audio/.
# C'est la seule table qui connaît l'arborescence des sons.
SOUND_FILES = {
    # --- Joueur ------------------------------------------------------------ #
    "footstep": "player/footstep.wav",
    "breathing": "player/breathing.wav",
    "pain": "player/pain.wav",
    # --- Objets ------------------------------------------------------------ #
    "potion_get": "items/potion/get.wav",
    "potion_use": "items/potion/use.wav",
    "key_get": "items/key/get.wav",
    "key_use": "items/key/use.wav",
    "torch_get": "items/torch/get.wav",
    "torch_use": "items/torch/use.wav",
    # Objet sans son dédié (le bouclier) : placeholder historique.
    "pickup": "pickup.wav",
    # --- Environnement ------------------------------------------------------ #
    "door_open": "misc/doors/open_wooden_door.wav",
    "door_locked": "misc/doors/door_locked.wav",
    "plate_press": "misc/plate/pressure_plate.wav",
    "plate_release": "misc/plate/release_pressure_plate.wav",
    "spike_strike": "misc/trap/spiketrap_open.wav",
    "arrow_shot": "misc/trap/arrow_shot.wav",          # placeholder de synthèse
    # --- Ambiance ----------------------------------------------------------- #
    "water_drop": "ambiance/water_drop.wav",
    "squeak": "ambiance/squeak.wav",
    "menu_music": "ambiance/mainmenu/mainmenu_sound.mp3",
    # --- Interface ---------------------------------------------------------- #
    "ui_hover": "menu/hover_button.wav",
    "ui_click": "menu/button_click.wav",
    # --- Le monstre ---------------------------------------------------------- #
    "alert_far": "monster/alerts/far_away.wav",
    "alert_near": "monster/alerts/mi_distance.wav",
    "alert_close": "monster/alerts/near.wav",
    "alert_released": "monster/alerts/now.wav",
    # Les deux sons ont ete echanges a la demande de l'equipe : `kill_sound`
    # annonce desormais le lacher, et `final_timer` accompagne le jumpscare.
    "monster_released": "monster/kill_sound.wav",
    "monster_kill": "monster/final_timer.wav",
    # --- Fin de partie -------------------------------------------------------- #
    "victory": "misc/victory.wav",                     # placeholder de synthèse
    "game_over": "misc/game_over.wav",                 # placeholder de synthèse
}

# Un grognement par palier de tension. Ces quatre sons sont EXACTEMENT les
# quatre murmures rouges affichés par l'ATH (voir monster_manager.STAGE_WHISPERS)
# : le joueur lit et entend la même information au même instant.
TENSION_CUES = {
    "far": "alert_far",            # "Quelque chose remue, loin dans la tour."
    "near": "alert_near",          # "Des griffes raclent la pierre. Plus pres."
    "close": "alert_close",        # "Des pas courent dans le noir."
    "released": "alert_released",  # "Elle est la."
}

# Sons d'ambiance tirés au hasard, dans le silence. Le tirage est PONDÉRÉ
# (`C.AUDIO_AMBIENCE_WEIGHTS`) : la goutte d'eau revient bien plus souvent que le
# grincement, qui dure dix secondes et lasserait à la même fréquence.
AMBIENCE_CUES = tuple(C.AUDIO_AMBIENCE_WEIGHTS)
AMBIENCE_WEIGHTS = tuple(C.AUDIO_AMBIENCE_WEIGHTS.values())

# Son de ramassage propre à chaque type d'objet. Un objet absent de cette table
# retombe sur le placeholder générique `pickup`.
ITEM_PICKUP_SOUNDS = {
    C.ITEM_VIAL: "potion_get",
    C.ITEM_KEY: "key_get",
    C.ITEM_TORCH: "torch_get",
}


class AudioManager:
    """Charge et joue les sons, en tolérant les fichiers manquants."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.master_volume = C.AUDIO_MASTER_VOLUME
        self._sounds: dict[str, arcade.Sound] = {}
        # Sons introuvables ou illisibles, retenus une fois pour toutes : une
        # boucle qui n'a pas pu demarrer est retentee a CHAQUE frame, et sans
        # cette memoire le jeu irait taper sur le disque soixante fois par
        # seconde pour un fichier qui n'existe pas.
        self._unavailable: set[str] = set()
        # Sons continus en cours, par CANAL : un canal ne porte qu'un son à la
        # fois ("music", "breathing"), ce qui évite d'empiler deux boucles l'une
        # sur l'autre après un changement d'écran.
        self._loops: dict[str, object] = {}
        self._rng = random.Random()

        # Ambiance aléatoire (gouttes, grincements).
        self._ambience_running = False
        self._ambience_timer = 0.0
        # Pas et respiration. Le premier souffle est tire au hasard lui aussi :
        # sinon chaque partie s'ouvrirait exactement sur le meme son.
        self._footstep_timer = 0.0
        self._breath_timer = self._rng.uniform(
            C.AUDIO_BREATH_RANDOM_MIN, C.AUDIO_BREATH_RANDOM_MAX
        )

    # ------------------------------------------------------------------ #
    # Sons ponctuels
    # ------------------------------------------------------------------ #
    def _get(self, name: str) -> arcade.Sound | None:
        """Charge un son à la demande ; renvoie None si le fichier n'existe pas."""
        if name in self._sounds:
            return self._sounds[name]
        if name in self._unavailable:
            return None
        filename = SOUND_FILES.get(name)
        path = C.AUDIO_DIR / filename if filename else None
        if path is None or not path.exists():
            self._unavailable.add(name)
            return None
        try:
            sound = arcade.Sound(str(path))
        except Exception:  # pragma: no cover - dépend du backend audio de la machine
            self._unavailable.add(name)
            return None
        self._sounds[name] = sound
        return sound

    def _volume_of(self, name: str, scale: float) -> float:
        """Volume final d'un son : mixage du jeu x réglage d'appel x volume général."""
        return C.AUDIO_VOLUMES.get(name, 1.0) * scale * self.master_volume

    def play(self, name: str, volume: float = 1.0, loop: bool = False):
        """
        Joue un son. `volume` est un COEFFICIENT appliqué au mixage de
        `C.AUDIO_VOLUMES` : 1.0 = volume prévu pour ce son, 0.5 = moitié moins.
        """
        if not self.enabled:
            return None
        sound = self._get(name)
        if sound is None:
            return None
        try:
            return sound.play(volume=self._volume_of(name, volume), loop=loop)
        except Exception:  # pragma: no cover
            return None

    def play_item_pickup(self, item_type: str) -> None:
        """Son de ramassage correspondant au type d'objet."""
        self.play(ITEM_PICKUP_SOUNDS.get(item_type, "pickup"))

    # ------------------------------------------------------------------ #
    # Sons continus (musique du menu, respiration)
    # ------------------------------------------------------------------ #
    def start_loop(self, channel: str, name: str, volume: float = 1.0) -> None:
        """Démarre un son en boucle sur un canal. Sans effet s'il tourne déjà."""
        if channel in self._loops:
            return
        player = self.play(name, volume=volume, loop=True)
        if player is not None:
            self._loops[channel] = (player, name)

    def stop_loop(self, channel: str) -> None:
        if channel not in self._loops:
            return
        player, _ = self._loops.pop(channel)
        try:
            player.pause()
            player.delete()
        except Exception:  # pragma: no cover
            pass

    def set_loop_volume(self, channel: str, volume: float) -> None:
        """Ajuste le volume d'une boucle en cours (coefficient, comme `play`)."""
        entry = self._loops.get(channel)
        if entry is None:
            return
        player, name = entry
        try:
            player.volume = self._volume_of(name, volume)
        except Exception:  # pragma: no cover
            pass

    def stop_all(self) -> None:
        """Coupe tous les sons continus : à appeler en quittant une vue."""
        for channel in list(self._loops):
            self.stop_loop(channel)

    def toggle_mute(self) -> bool:
        """
        Coupe ou rétablit tout le son. Renvoie True si le son est désormais coupé.

        Utile en jam : on montre le jeu à quelqu'un dans une salle bruyante, ou
        on le laisse tourner sur un stand sans hurler. L'ambiance reste ARMÉE
        pendant la coupure, elle reprend donc d'elle-même au rétablissement.
        """
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_all()
        return not self.enabled

    # ------------------------------------------------------------------ #
    # Musique du menu
    # ------------------------------------------------------------------ #
    def start_menu_music(self) -> None:
        """Musique de l'écran d'accueil, qui court aussi sur les écrans de fin."""
        self.start_loop("music", "menu_music")

    def stop_menu_music(self) -> None:
        self.stop_loop("music")

    # ------------------------------------------------------------------ #
    # Ambiance : le silence, troué au hasard
    # ------------------------------------------------------------------ #
    def start_ambience(self) -> None:
        """Arme l'ambiance aléatoire (aucun son n'est joué tout de suite)."""
        self._ambience_running = True
        self._ambience_timer = self._next_ambience_delay()

    def stop_ambience(self) -> None:
        self._ambience_running = False
        self.stop_all()

    def _next_ambience_delay(self) -> float:
        return self._rng.uniform(C.AUDIO_AMBIENCE_MIN_DELAY, C.AUDIO_AMBIENCE_MAX_DELAY)

    def update_ambience(self, delta_time: float) -> None:
        """Laisse tomber une goutte ou grincer une porte, de loin en loin."""
        if not self._ambience_running:
            return
        self._ambience_timer -= delta_time
        if self._ambience_timer > 0:
            return
        self._ambience_timer = self._next_ambience_delay()
        self.play(self._rng.choices(AMBIENCE_CUES, weights=AMBIENCE_WEIGHTS)[0])

    # ------------------------------------------------------------------ #
    # Pas et respiration du joueur
    # ------------------------------------------------------------------ #
    def update_footsteps(self, delta_time: float, moving: bool) -> None:
        """Un pas à cadence fixe tant que le joueur se déplace."""
        if not moving:
            # Le prochain pas sonne dès le redémarrage : sans cela, repartir
            # après un arrêt donnait un demi-pas de silence.
            self._footstep_timer = 0.0
            return
        self._footstep_timer -= delta_time
        if self._footstep_timer <= 0:
            self._footstep_timer = C.AUDIO_FOOTSTEP_INTERVAL
            self.play("footstep")

    def update_breathing(self, delta_time: float, stage: str, tension: float) -> None:
        """
        Deux régimes de respiration.

          - tant que la créature est loin : un souffle de temps en temps, tiré
            au hasard, qui rappelle que le personnage est vivant et a peur ;
          - à partir du palier `near` : un halètement CONTINU, de plus en plus
            fort. C'est un des trois signaux qui disent au joueur qu'il n'a
            presque plus de temps, à la place d'un compte à rebours.
        """
        if stage in C.AUDIO_BREATH_PANIC_STAGES:
            self.start_loop("breathing", "breathing")
            # De 0,7 au palier "near" à 1,0 une fois la bête lâchée.
            self.set_loop_volume("breathing", 0.7 + 0.3 * tension)
            return

        self.stop_loop("breathing")
        self._breath_timer -= delta_time
        if self._breath_timer <= 0:
            self._breath_timer = self._rng.uniform(
                C.AUDIO_BREATH_RANDOM_MIN, C.AUDIO_BREATH_RANDOM_MAX
            )
            self.play("breathing", volume=C.AUDIO_BREATH_CALM_VOLUME)

    # ------------------------------------------------------------------ #
    # Signaux de la créature
    # ------------------------------------------------------------------ #
    def play_tension_cue(self, stage: str) -> None:
        """Grognement du palier franchi, plus la sonnerie du lâcher."""
        cue = TENSION_CUES.get(stage)
        if cue:
            self.play(cue)
        if stage == "released":
            # Superposé à l'alerte : le sursis est fini, elle est dans le
            # labyrinthe. C'est le seul moment du jeu où deux sons se cumulent
            # volontairement.
            self.play("monster_released")
