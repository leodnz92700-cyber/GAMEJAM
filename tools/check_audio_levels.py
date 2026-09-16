"""
Fichier : tools/check_audio_levels.py
Auteur : base technique (game jam)

Description :
Verifie que tous les sons du jeu sortent au MEME niveau a l'oreille.

    .venv/bin/python tools/check_audio_levels.py

Le probleme qu'il resout : les fichiers livres par le sound design n'ont pas du
tout le meme niveau d'enregistrement — il y avait 34 dB d'ecart entre le clic de
menu et la respiration, soit un facteur 50. Regler les volumes "au jugé" dans
`constants.AUDIO_VOLUMES` ne peut pas marcher, parce qu'un meme coefficient
donne un resultat completement different selon le fichier.

La methode :

  1. on mesure le niveau REEL de chaque fichier (RMS, uniquement sur sa partie
     sonore : une longue queue de silence fausserait la mesure) ;
  2. chaque son a un ROLE, qui dit a quel volume il doit sortir dans le jeu.
     Un pas qui sonne trois fois par seconde n'a pas a sortir aussi fort qu'un
     grognement qui previent le joueur qu'il va mourir ;
  3. le coefficient ideal est donc `cible / (niveau du fichier x volume general)`,
     et c'est ce que doit contenir `AUDIO_VOLUMES`.

**A relancer apres avoir remplace un fichier audio** : un nouveau son enregistre
plus fort ou plus faible que l'ancien desequilibre tout le mixage, sans que rien
ne le signale en jeu.

Quand un coefficient ideal depasse 1.0, c'est que le fichier est trop FAIBLE
pour etre rattrape : on ne peut pas monter le volume au-dela du maximum. Il faut
alors reamplifier le fichier lui-meme (le script le dit, et donne le gain).
"""
from __future__ import annotations

import math
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import constants as C                                  # noqa: E402
from src.mechanics.audio_manager import SOUND_FILES             # noqa: E402

# Niveau de sortie vise, par role. Ce sont des RMS apres coefficient et volume
# general : c'est ce que le joueur entend vraiment.
TARGETS = {
    "repetitif": 0.020,   # joue plusieurs fois par seconde : doit rester en fond
    "discret": 0.030,     # decor et ambiance, presents sans attirer l'oreille
    "normal": 0.045,      # les actions du joueur : ramasser, ouvrir, planter
    "marquant": 0.065,    # ce qui doit faire sursauter ou prevenir d'un danger
    "boucle": 0.040,      # sons continus : ils fatiguent vite s'ils sont forts
    "souffle": 0.020,     # la respiration : un fond permanent, elle doit rester sous tout
}

# Role de chaque son. Une modification ici doit etre reportee dans
# `AUDIO_VOLUMES`, et ce script est justement la pour signaler l'oubli.
ROLES = {
    "footstep": "repetitif",
    "arrow_shot": "repetitif",
    "ui_hover": "repetitif",
    "spike_strike": "discret",
    "plate_press": "discret",
    "plate_release": "discret",
    "water_drop": "discret",
    "squeak": "discret",
    "potion_get": "normal",
    "key_get": "normal",
    "torch_get": "normal",
    "torch_use": "normal",
    "key_use": "normal",
    "pickup": "normal",
    "door_open": "normal",
    "door_locked": "normal",
    "ui_click": "normal",
    "potion_use": "marquant",
    "pain": "marquant",
    "monster_kill": "marquant",
    "monster_released": "marquant",
    "alert_far": "marquant",
    "alert_near": "marquant",
    "alert_close": "marquant",
    "alert_released": "marquant",
    "victory": "marquant",
    "game_over": "marquant",
    "breathing": "souffle",
    "monster_chase": "boucle",
    "menu_music": "boucle",   # MP3 : non mesurable ici, se regle a l'oreille
}

TOLERANCE_DB = 2.5          # au-dela, l'ecart s'entend


def read_samples(path: Path) -> list[float]:
    """Echantillons d'un WAV, ramenes a [-1, 1], quels que soient sa taille et son format."""
    handle = wave.open(str(path), "rb")
    frames, channels, width = handle.getnframes(), handle.getnchannels(), handle.getsampwidth()
    raw = handle.readframes(frames)
    handle.close()

    # Un seul canal suffit pour mesurer un niveau, et c'est bien plus rapide.
    step = width * channels
    full_scale = float(1 << (width * 8 - 1))
    values = []
    for index in range(0, len(raw) - step + 1, step):
        chunk = raw[index:index + width]
        sample = int.from_bytes(chunk, "little", signed=True) if width > 1 else chunk[0] - 128
        values.append(sample / full_scale)
    return values


def measure(values: list[float]) -> tuple[float, float]:
    """
    Pic et RMS d'un son, le RMS pris sur sa seule partie AUDIBLE.

    Un RMS calcule sur toute la duree punit les fichiers a longue queue de
    silence : deux sons aussi forts a l'oreille donnent alors des chiffres tres
    differents, simplement parce que l'un traine dix secondes de blanc.
    """
    peak = max(abs(value) for value in values) or 1e-9
    gate = peak * 0.08
    audible = [value for value in values if abs(value) > gate] or values
    return peak, math.sqrt(sum(value * value for value in audible) / len(audible))


def main() -> None:
    print(f"volume general : {C.AUDIO_MASTER_VOLUME}\n")
    header = f"{'son':<18} {'role':<10} {'RMS fichier':>11} {'coef':>6} {'ideal':>6} {'sortie dB':>10}"
    print(header)
    print("-" * len(header))

    problems: list[str] = []
    outputs: list[tuple[str, float]] = []

    for name, relative in sorted(SOUND_FILES.items()):
        path = C.AUDIO_DIR / relative
        if not path.exists():
            problems.append(f"{name} : fichier absent ({relative})")
            continue
        if path.suffix.lower() != ".wav":
            # La musique du menu est un MP3 : elle se regle a l'oreille, et elle
            # est de toute facon seule sur son ecran.
            continue
        role = ROLES.get(name)
        if role is None:
            problems.append(f"{name} : aucun role declare dans ce script")
            continue

        peak, rms = measure(read_samples(path))
        coefficient = C.AUDIO_VOLUMES.get(name, 1.0)
        target = TARGETS[role]
        ideal = target / (rms * C.AUDIO_MASTER_VOLUME)
        output = rms * coefficient * C.AUDIO_MASTER_VOLUME
        outputs.append((name, output))

        print(f"{name:<18} {role:<10} {rms:>11.4f} {coefficient:>6.3f} {ideal:>6.3f} "
              f"{20 * math.log10(output):>9.1f}")

        if ideal > 1.0:
            gain = ideal / min(1.0, 0.95 / peak)
            problems.append(
                f"{name} : fichier trop FAIBLE ({relative}). Meme a plein volume il "
                f"sortira {20 * math.log10(target / (rms * C.AUDIO_MASTER_VOLUME)):.1f} dB "
                f"trop bas. Reamplifiez-le d'environ x{ideal:.1f} "
                f"(sans clipper : x{0.95 / peak:.1f} maximum)."
                if gain > 1.0 else f"{name} : fichier trop faible ({relative})."
            )
            continue

        drift = 20 * math.log10(output / target)
        if abs(drift) > TOLERANCE_DB:
            problems.append(
                f"{name} : sort {drift:+.1f} dB par rapport a son role "
                f"« {role} ». Mettez AUDIO_VOLUMES[\"{name}\"] = {ideal:.3f}"
            )

    if outputs:
        loudest = max(outputs, key=lambda item: item[1])
        quietest = min(outputs, key=lambda item: item[1])
        spread = 20 * math.log10(loudest[1] / quietest[1])
        print(f"\necart entre le plus fort ({loudest[0]}) et le plus faible "
              f"({quietest[0]}) : {spread:.1f} dB")

    if problems:
        print("\nPROBLEMES :")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("\nOK : tous les sons sortent au niveau prevu par leur role.")
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
