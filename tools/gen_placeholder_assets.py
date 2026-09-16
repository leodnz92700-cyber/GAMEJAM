"""
Fichier : tools/gen_placeholder_assets.py
Auteur : base technique (game jam)

Description :
Génère les assets que le pack graphique ne fournit PAS : les sons (synthèse pure
en Python), le dégradé radial du moteur de lumière, et le carreau du piège à
fléchettes.

    python tools/gen_placeholder_assets.py

Tout le reste des sprites vient du pack Dungeons & Pixels : voir
`tools/import_pack_assets.py`.

Les sons sont des PLACEHOLDERS. Quand les sound designers livrent leurs vrais
fichiers, il suffit de les déposer dans `assets/audio/` sous les mêmes noms et de
ne plus relancer ce script.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "assets" / "sprites"
AUDIO = ROOT / "assets" / "audio"
MAPS = ROOT / "assets" / "maps"

TILE = 32

# Ordre des tuiles dans le tileset placeholder (l'index = id local Tiled).
# 0 = sol, 1 = mur, 2 = sol de la zone de sortie, 3 = sol "dalle" décoratif.
TILESET_COLORS = [
    (44, 42, 54),    # 0 floor
    (152, 144, 188),  # 1 wall
    (64, 104, 84),   # 2 exit floor
    (48, 46, 60),    # 3 floor alt
]


# --------------------------------------------------------------------------- #
# Sprites non fournis par le pack graphique
# --------------------------------------------------------------------------- #
def make_light_gradient(size: int = 512) -> None:
    """
    Dégradé radial utilisé par le moteur de lumière pour la passe de lueur.

    Le RGB est blanc, seul le canal alpha porte l'information : 255 au centre
    (zone totalement éclairée) et 0 au bord.
    """
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    pixels = img.load()
    radius = size / 2
    for y in range(size):
        for x in range(size):
            distance = math.hypot(x - radius + 0.5, y - radius + 0.5) / radius
            if distance >= 1.0:
                continue
            # Falloff doux : plein feu au centre, extinction progressive au bord.
            alpha = (1.0 - distance) ** 1.7
            pixels[x, y] = (255, 255, 255, int(alpha * 255))
    img.save(SPRITES / "light_gradient.png")


# --------------------------------------------------------------------------- #
# Sons de synthèse
# --------------------------------------------------------------------------- #
SAMPLE_RATE = 22050


def write_wav(name: str, samples: list[float]) -> None:
    """Écrit une liste de flottants [-1, 1] en WAV mono 16 bits."""
    path = AUDIO / name
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, value)) * 32000)) for value in samples
        )
        handle.writeframes(frames)


def noise(seed: int):
    """Générateur de bruit déterministe (pas de numpy dans les dépendances)."""
    state = seed

    def next_value() -> float:
        nonlocal state
        state = (1103515245 * state + 12345) % (1 << 31)
        return (state / (1 << 30)) - 1.0

    return next_value


def envelope(index: int, total: int, attack: float = 0.05, release: float = 0.4) -> float:
    position = index / total
    if position < attack:
        return position / attack
    if position > 1.0 - release:
        return (1.0 - position) / release
    return 1.0


def make_sounds() -> None:
    rand = noise(7)

    def sample_count(seconds: float) -> int:
        return int(SAMPLE_RATE * seconds)

    # Ambiance : nappe grave bouclable.
    total = sample_count(6.0)
    ambience = []
    for i in range(total):
        t = i / SAMPLE_RATE
        value = (
            0.25 * math.sin(2 * math.pi * 55 * t)
            + 0.12 * math.sin(2 * math.pi * 82.5 * t + math.sin(t * 0.4))
            + 0.05 * rand()
        )
        # Fondu croisé aux extrémités pour que la boucle ne claque pas.
        fade = min(1.0, i / sample_count(0.5), (total - i) / sample_count(0.5))
        ambience.append(value * fade * 0.6)
    write_wav("ambience_drone.wav", ambience)

    # Grondement lointain (premier avertissement).
    total = sample_count(2.4)
    growl = []
    for i in range(total):
        t = i / SAMPLE_RATE
        base = math.sin(2 * math.pi * (48 + 6 * math.sin(2 * math.pi * 1.3 * t)) * t)
        growl.append((0.6 * base + 0.25 * rand()) * envelope(i, total, 0.2, 0.5) * 0.5)
    write_wav("growl_far.wav", growl)

    # Grattements contre les murs (avertissement intermédiaire).
    total = sample_count(1.2)
    scratch = []
    for i in range(total):
        t = i / SAMPLE_RATE
        burst = 1.0 if int(t * 26) % 2 == 0 else 0.25
        scratch.append(rand() * burst * envelope(i, total, 0.05, 0.3) * 0.45)
    write_wav("scratch.wav", scratch)

    # Pas qui se rapprochent (avertissement tardif).
    total = sample_count(1.6)
    steps = []
    for i in range(total):
        t = i / SAMPLE_RATE
        local = (t % 0.4) / 0.4
        hit = math.exp(-local * 18) * math.sin(2 * math.pi * 90 * t)
        steps.append((hit + 0.1 * rand() * math.exp(-local * 12)) * 0.7)
    write_wav("steps_close.wav", steps)

    # Battement de coeur (la bête est lâchée).
    total = sample_count(1.0)
    heartbeat = []
    for i in range(total):
        t = i / SAMPLE_RATE
        beat = 0.0
        for offset in (0.0, 0.28):
            local = t - offset
            if 0 <= local < 0.25:
                beat += math.exp(-local * 22) * math.sin(2 * math.pi * 52 * local)
        heartbeat.append(beat * 0.8)
    write_wav("heartbeat.wav", heartbeat)

    # Mort dévorée.
    total = sample_count(1.4)
    devour = []
    for i in range(total):
        t = i / SAMPLE_RATE
        pitch = 320 * math.exp(-t * 2.2)
        devour.append(
            (0.5 * math.sin(2 * math.pi * pitch * t) + 0.5 * rand())
            * envelope(i, total, 0.01, 0.6)
        )
    write_wav("devoured.wav", devour)

    # Mort volontaire (fiole) : descente douce.
    total = sample_count(1.0)
    vial = []
    for i in range(total):
        t = i / SAMPLE_RATE
        pitch = 420 * math.exp(-t * 1.6)
        vial.append(0.5 * math.sin(2 * math.pi * pitch * t) * envelope(i, total, 0.02, 0.6))
    write_wav("death_vial.wav", vial)

    # Petits sons d'interaction.
    for name, freq, seconds in (
        ("pickup.wav", 660, 0.18),
        ("door_open.wav", 180, 0.5),
        ("torch_place.wav", 320, 0.3),
        ("plate_click.wav", 900, 0.12),
        ("trap_trigger.wav", 140, 0.45),
    ):
        total = sample_count(seconds)
        buffer = []
        for i in range(total):
            t = i / SAMPLE_RATE
            buffer.append(
                0.5 * math.sin(2 * math.pi * freq * t) * envelope(i, total, 0.02, 0.5)
            )
        write_wav(name, buffer)


def main() -> None:
    for folder in (SPRITES, AUDIO, MAPS):
        folder.mkdir(parents=True, exist_ok=True)
    make_light_gradient()
    make_sounds()
    print(f"Assets placeholder générés dans {SPRITES} et {AUDIO}")


if __name__ == "__main__":
    main()
