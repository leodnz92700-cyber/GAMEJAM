"""
Fichier : audio_manager.py
Auteur : base technique (game jam)

Description :
Point d'entrée unique pour tout le son. Les fichiers actuels sont des
PLACEHOLDERS générés par `tools/gen_placeholder_assets.py` : remplacez-les par
les vrais sons en gardant les mêmes noms et rien d'autre ne bouge.

Le son n'est pas décoratif dans ce jeu : c'est lui qui remplace le compte à
rebours. `play_tension_cue` est appelé par `monster_manager` à chaque palier
d'approche de la créature.
"""
from __future__ import annotations

import arcade

from src import constants as C

# Nom logique -> fichier dans assets/audio/
SOUND_FILES = {
    "ambience": "ambience_drone.wav",
    "growl_far": "growl_far.wav",
    "scratch": "scratch.wav",
    "steps_close": "steps_close.wav",
    "heartbeat": "heartbeat.wav",
    "devoured": "devoured.wav",
    "death_vial": "death_vial.wav",
    "pickup": "pickup.wav",
    "door_open": "door_open.wav",
    "torch_place": "torch_place.wav",
    "plate_click": "plate_click.wav",
    "trap_trigger": "trap_trigger.wav",
}

# Son joué quand la créature franchit un palier de tension (voir constants).
TENSION_CUES = {
    "far": "growl_far",
    "near": "scratch",
    "close": "steps_close",
    "released": "heartbeat",
}


class AudioManager:
    """Charge et joue les sons, en tolérant les fichiers manquants."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.master_volume = 0.7
        self._sounds: dict[str, arcade.Sound] = {}
        self._ambience_player = None

    def _get(self, name: str) -> arcade.Sound | None:
        """Charge un son à la demande ; renvoie None si le fichier n'existe pas."""
        if name in self._sounds:
            return self._sounds[name]
        filename = SOUND_FILES.get(name)
        if not filename:
            return None
        path = C.AUDIO_DIR / filename
        if not path.exists():
            return None
        try:
            sound = arcade.Sound(str(path))
        except Exception:  # pragma: no cover - dépend du backend audio de la machine
            return None
        self._sounds[name] = sound
        return sound

    def play(self, name: str, volume: float = 1.0, loop: bool = False):
        if not self.enabled:
            return None
        sound = self._get(name)
        if sound is None:
            return None
        try:
            return sound.play(volume=volume * self.master_volume, loop=loop)
        except Exception:  # pragma: no cover
            return None

    # ------------------------------------------------------------------ #
    # Ambiance de fond
    # ------------------------------------------------------------------ #
    def start_ambience(self) -> None:
        if self._ambience_player is not None:
            return
        self._ambience_player = self.play("ambience", volume=0.45, loop=True)

    def stop_ambience(self) -> None:
        if self._ambience_player is None:
            return
        try:
            self._ambience_player.pause()
            self._ambience_player.delete()
        except Exception:  # pragma: no cover
            pass
        self._ambience_player = None

    def set_ambience_intensity(self, intensity: float) -> None:
        """
        Monte le volume de la nappe au fur et à mesure que la créature approche.

        `intensity` va de 0 (début de vie) à 1 (elle est lâchée).
        """
        if self._ambience_player is None:
            return
        try:
            self._ambience_player.volume = (0.35 + 0.45 * intensity) * self.master_volume
        except Exception:  # pragma: no cover
            pass

    # ------------------------------------------------------------------ #
    # Signaux de la créature
    # ------------------------------------------------------------------ #
    def play_tension_cue(self, stage: str) -> None:
        cue = TENSION_CUES.get(stage)
        if cue:
            self.play(cue, volume=0.9)
